# Скрипт для деплоя проекта на сервер через SSH
# Использование: .\deploy_to_server.ps1

param(
    [string]$ServerHost = "nyx",
    [string]$RemotePath = "~/english_lessons",
    [string]$SSHConfig = "$env:USERPROFILE\.ssh\config",
    [switch]$SkipBackup = $false,
    [switch]$SkipMigrations = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== Деплой проекта на сервер ===" -ForegroundColor Cyan
Write-Host ""

# Проверка SSH подключения
Write-Host "Проверка SSH подключения к $ServerHost..." -ForegroundColor Yellow
$sshTest = & "C:\Windows\System32\OpenSSH\ssh.exe" -F $SSHConfig -o ConnectTimeout=5 $ServerHost "echo 'SSH connection OK'" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка подключения к серверу!" -ForegroundColor Red
    Write-Host $sshTest -ForegroundColor Red
    exit 1
}
Write-Host "✅ SSH подключение успешно" -ForegroundColor Green
Write-Host ""

# Получаем информацию о сервере
Write-Host "Информация о сервере:" -ForegroundColor Yellow
$serverInfo = & "C:\Windows\System32\OpenSSH\ssh.exe" -F $SSHConfig $ServerHost "uname -a; python3 --version 2>&1 || echo 'Python не найден'; which git || echo 'Git не найден'"
Write-Host $serverInfo
Write-Host ""

# Создаем временную директорию для архива
$tempDir = [System.IO.Path]::GetTempPath()
$archiveName = "english_lessons_$(Get-Date -Format 'yyyyMMdd_HHmmss').tar.gz"
$archivePath = Join-Path $tempDir $archiveName

Write-Host "Создание архива проекта..." -ForegroundColor Yellow
# Исключаем ненужные файлы из архива
$excludePatterns = @(
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".git",
    "venv",
    "env",
    ".env",
    "db.sqlite3",
    "temp_audio",
    "videos",
    ".cursor",
    "*.log"
)

# Используем tar для создания архива (если доступен) или 7zip
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

# Создаем список файлов для архива
$filesToArchive = Get-ChildItem -Recurse -File | Where-Object {
    $shouldInclude = $true
    foreach ($pattern in $excludePatterns) {
        if ($_.FullName -like "*$pattern*") {
            $shouldInclude = $false
            break
        }
    }
    return $shouldInclude
}

Write-Host "Архивирование $($filesToArchive.Count) файлов..." -ForegroundColor Yellow

# Копируем файлы во временную директорию
$tempProjectDir = Join-Path $tempDir "english_lessons_temp"
if (Test-Path $tempProjectDir) {
    Remove-Item -Recurse -Force $tempProjectDir
}
New-Item -ItemType Directory -Path $tempProjectDir | Out-Null

foreach ($file in $filesToArchive) {
    $relativePath = $file.FullName.Substring($projectRoot.Length + 1)
    $destPath = Join-Path $tempProjectDir $relativePath
    $destDir = Split-Path -Parent $destPath
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    Copy-Item $file.FullName $destPath -Force
}

# Создаем tar.gz архив
Write-Host "Создание tar.gz архива..." -ForegroundColor Yellow
Set-Location $tempDir
tar -czf $archiveName -C $tempProjectDir . 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка создания архива!" -ForegroundColor Red
    exit 1
}

$archiveSize = (Get-Item $archivePath).Length / 1MB
Write-Host "✅ Архив создан: $archiveName ($([math]::Round($archiveSize, 2)) MB)" -ForegroundColor Green
Write-Host ""

# Копируем архив на сервер
Write-Host "Копирование архива на сервер..." -ForegroundColor Yellow
# Используем абсолютный путь через $HOME для надежности
$remoteArchivePath = "english_lessons_archive.tar.gz"
$remoteArchiveFullPath = "`$HOME/english_lessons_archive.tar.gz"
$scpResult = & "C:\Windows\System32\OpenSSH\scp.exe" -F $SSHConfig $archivePath "${ServerHost}:${remoteArchivePath}" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка копирования архива на сервер!" -ForegroundColor Red
    Write-Host $scpResult -ForegroundColor Red
    exit 1
}

# Проверяем, что архив действительно скопирован
Write-Host "Проверка архива на сервере..." -ForegroundColor Yellow
$checkArchive = & "C:\Windows\System32\OpenSSH\ssh.exe" -F $SSHConfig $ServerHost "test -f `$HOME/english_lessons_archive.tar.gz && echo 'OK' || echo 'NOT_FOUND'" 2>&1
if ($checkArchive -notmatch "OK") {
    Write-Host "❌ Архив не найден на сервере после копирования!" -ForegroundColor Red
    Write-Host "Проверка: $checkArchive" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Архив скопирован и проверен на сервере" -ForegroundColor Green
Write-Host ""

# Выполняем команды на сервере
Write-Host "Выполнение команд на сервере..." -ForegroundColor Yellow

# Подготавливаем значения для bash скрипта
$skipBackupValue = if ($SkipBackup) { "true" } else { "false" }
$skipMigrationsValue = if ($SkipMigrations) { "true" } else { "false" }

$deployScript = @"
#!/bin/bash
set -e

REMOTE_PATH="$RemotePath"
ARCHIVE_PATH="`$HOME/english_lessons_archive.tar.gz"
SKIP_BACKUP="$skipBackupValue"
SKIP_MIGRATIONS="$skipMigrationsValue"

echo "=== Развертывание проекта ==="

# Создаем директорию проекта
mkdir -p `$REMOTE_PATH
cd `$REMOTE_PATH

# Создаем резервную копию (если существует)
if [ -d "english_lessons" ] && [ "`$SKIP_BACKUP" != "true" ]; then
    echo "Создание резервной копии..."
    BACKUP_NAME="english_lessons_backup_`$(date +%Y%m%d_%H%M%S)"
    cp -r english_lessons "`$BACKUP_NAME" || true
    echo "✅ Резервная копия создана: `$BACKUP_NAME"
fi

# Распаковываем архив
echo "Распаковка архива..."
# Проверяем существование архива
if [ ! -f "`$ARCHIVE_PATH" ]; then
    echo "❌ Ошибка: архив не найден по пути: `$ARCHIVE_PATH"
    echo "Проверяем альтернативные пути..."
    # Пробуем найти архив
    if [ -f "`$HOME/english_lessons_archive.tar.gz" ]; then
        ARCHIVE_PATH="`$HOME/english_lessons_archive.tar.gz"
        echo "✅ Архив найден: `$ARCHIVE_PATH"
    else
        echo "❌ Архив не найден ни в одном из мест!"
        ls -la `$HOME/ | grep english_lessons || true
        exit 1
    fi
fi

mkdir -p english_lessons
cd english_lessons
tar -xzf "`$ARCHIVE_PATH"
cd ..

# Удаляем архив
rm -f "`$ARCHIVE_PATH"

# Переходим в директорию проекта
cd english_lessons

# Создаем виртуальное окружение (если не существует)
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение и устанавливаем зависимости
echo "Установка зависимостей..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Применяем миграции (если не пропущено)
if [ "`$SKIP_MIGRATIONS" != "true" ]; then
    echo "Применение миграций..."
    python manage.py migrate --noinput
fi

# Собираем статические файлы
echo "Сбор статических файлов..."
python manage.py collectstatic --noinput || echo "⚠️ collectstatic пропущен (возможно, не настроен STATIC_ROOT)"

echo ""
echo "✅ Деплой завершен успешно!"
echo "Путь к проекту: `$REMOTE_PATH/english_lessons"
"@

# Сохраняем скрипт во временный файл с правильной кодировкой (UTF-8 без BOM, LF)
$deployScriptPath = Join-Path $tempDir "deploy_script.sh"
# Конвертируем CRLF в LF и сохраняем в UTF-8 без BOM
$deployScriptUnix = $deployScript -replace "`r`n", "`n"
[System.IO.File]::WriteAllText($deployScriptPath, $deployScriptUnix, [System.Text.UTF8Encoding]::new($false))

# Копируем скрипт на сервер и выполняем
Write-Host "Запуск скрипта развертывания на сервере..." -ForegroundColor Yellow
& "C:\Windows\System32\OpenSSH\scp.exe" -F $SSHConfig $deployScriptPath "${ServerHost}:~/deploy_script.sh" | Out-Null
$deployOutput = & "C:\Windows\System32\OpenSSH\ssh.exe" -F $SSHConfig $ServerHost "chmod +x ~/deploy_script.sh && bash ~/deploy_script.sh && rm ~/deploy_script.sh"
Write-Host $deployOutput

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Деплой завершен успешно!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Следующие шаги:" -ForegroundColor Cyan
    Write-Host "1. Подключитесь к серверу: ssh -F $SSHConfig $ServerHost" -ForegroundColor White
    Write-Host "2. Перейдите в директорию: cd $RemotePath/english_lessons" -ForegroundColor White
    Write-Host "3. Создайте файл .env с настройками (скопируйте с локальной машины)" -ForegroundColor White
    Write-Host "4. Настройте базу данных PostgreSQL" -ForegroundColor White
    Write-Host "5. Запустите сервер: source venv/bin/activate && python manage.py runserver 0.0.0.0:8000" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Ошибка при деплое!" -ForegroundColor Red
    exit 1
}

# Очистка
Write-Host ""
Write-Host "Очистка временных файлов..." -ForegroundColor Yellow
Remove-Item -Recurse -Force $tempProjectDir -ErrorAction SilentlyContinue
Remove-Item -Force $archivePath -ErrorAction SilentlyContinue
Remove-Item -Force $deployScriptPath -ErrorAction SilentlyContinue

Write-Host "✅ Готово!" -ForegroundColor Green

