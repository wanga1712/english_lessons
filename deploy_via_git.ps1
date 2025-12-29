# Скрипт для деплоя через Git
# Использование: .\deploy_via_git.ps1

param(
    [string]$ServerHost = "nyx",
    [string]$RemotePath = "~/english_lessons",
    [string]$SSHConfig = "$env:USERPROFILE\.ssh\config",
    [string]$GitRepo = "",  # URL репозитория Git (если пусто, будет использован текущий)
    [switch]$SkipMigrations = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== Деплой через Git ===" -ForegroundColor Cyan
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

# Если GitRepo не указан, пытаемся получить из текущего репозитория
if ([string]::IsNullOrEmpty($GitRepo)) {
    Write-Host "Определение URL Git репозитория..." -ForegroundColor Yellow
    $gitRemote = git remote get-url origin 2>&1
    if ($LASTEXITCODE -eq 0) {
        $GitRepo = $gitRemote.Trim()
        Write-Host "✅ Найден репозиторий: $GitRepo" -ForegroundColor Green
    } else {
        Write-Host "❌ Не удалось определить Git репозиторий!" -ForegroundColor Red
        Write-Host "Укажите URL репозитория: .\deploy_via_git.ps1 -GitRepo 'https://github.com/user/repo.git'" -ForegroundColor Yellow
        exit 1
    }
}

# Подготавливаем значения для bash скрипта
$skipMigrationsValue = if ($SkipMigrations) { "true" } else { "false" }

# Создаем bash скрипт с правильным экранированием
$bashScriptLines = @(
    "#!/bin/bash",
    "set -e",
    "",
    "REMOTE_PATH=`"$RemotePath`"",
    "GIT_REPO=`"$GitRepo`"",
    "SKIP_MIGRATIONS=`"$skipMigrationsValue`"",
    "",
    "echo `"=== Развертывание проекта через Git ===`"",
    "",
    "# Создаем директорию проекта",
    "mkdir -p `$REMOTE_PATH",
    "cd `$REMOTE_PATH",
    "",
    "# Клонируем или обновляем репозиторий",
    "if [ -d `"english_lessons`" ]; then",
    "    echo `"Обновление существующего репозитория...`"",
    "    cd english_lessons",
    "    git fetch origin",
    "    git reset --hard origin/main 2>/dev/null || git reset --hard origin/master 2>/dev/null || true",
    "    git pull",
    "else",
    "    echo `"Клонирование репозитория...`"",
    "    git clone `"`$GIT_REPO`" english_lessons",
    "    cd english_lessons",
    "fi",
    "",
    "# Создаем виртуальное окружение (если не существует)",
    "if [ ! -d `"venv`" ]; then",
    "    echo `"Создание виртуального окружения...`"",
    "    python3 -m venv venv",
    "fi",
    "",
    "# Активируем виртуальное окружение и устанавливаем зависимости",
    "echo `"Установка зависимостей...`"",
    "source venv/bin/activate",
    "pip install --upgrade pip",
    "pip install -r requirements.txt",
    "",
    "# Применяем миграции (если не пропущено)",
    "if [ `"`$SKIP_MIGRATIONS`" != `"true`" ]; then",
    "    echo `"Применение миграций...`"",
    "    python manage.py migrate --noinput",
    "fi",
    "",
    "# Собираем статические файлы",
    "echo `"Сбор статических файлов...`"",
    "python manage.py collectstatic --noinput || echo `"⚠️ collectstatic пропущен (возможно, не настроен STATIC_ROOT)`"",
    "",
    "echo `"`"",
    "echo `"✅ Деплой завершен успешно!`"",
    "echo `"Путь к проекту: `$REMOTE_PATH/english_lessons`""
)

$deployScript = $bashScriptLines -join "`n"

# Сохраняем скрипт во временный файл с правильной кодировкой
$tempDir = [System.IO.Path]::GetTempPath()
$deployScriptPath = Join-Path $tempDir "deploy_git_script_$(Get-Date -Format 'yyyyMMddHHmmss').sh"
[System.IO.File]::WriteAllText($deployScriptPath, $deployScript, [System.Text.UTF8Encoding]::new($false))

# Копируем скрипт на сервер и выполняем
Write-Host "Запуск скрипта развертывания на сервере..." -ForegroundColor Yellow
& "C:\Windows\System32\OpenSSH\scp.exe" -F $SSHConfig $deployScriptPath "${ServerHost}:~/deploy_git_script.sh" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка копирования скрипта на сервер!" -ForegroundColor Red
    exit 1
}

$deployOutput = & "C:\Windows\System32\OpenSSH\ssh.exe" -F $SSHConfig $ServerHost "chmod +x ~/deploy_git_script.sh; bash ~/deploy_git_script.sh; rm ~/deploy_git_script.sh"
Write-Host $deployOutput

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Деплой завершен успешно!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Следующие шаги:" -ForegroundColor Cyan
    Write-Host "1. Подключитесь к серверу: ssh -F $SSHConfig $ServerHost" -ForegroundColor White
    Write-Host "2. Перейдите в директорию: cd $RemotePath/english_lessons" -ForegroundColor White
    Write-Host "3. Создайте файл .env с настройками" -ForegroundColor White
    Write-Host "4. Настройте базу данных PostgreSQL" -ForegroundColor White
    Write-Host "5. Запустите сервер: source venv/bin/activate && python manage.py runserver 0.0.0.0:8000" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Ошибка при деплое!" -ForegroundColor Red
    exit 1
}

# Удаляем временный файл
Remove-Item -Force $deployScriptPath -ErrorAction SilentlyContinue

Write-Host "✅ Готово!" -ForegroundColor Green
