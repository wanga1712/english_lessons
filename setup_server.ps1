# Скрипт для первоначальной настройки сервера
# Использование: .\setup_server.ps1

param(
    [string]$ServerHost = "nyx",
    [string]$SSHConfig = "$env:USERPROFILE\.ssh\config"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Первоначальная настройка сервера ===" -ForegroundColor Cyan
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

# Скрипт настройки для сервера
$setupScript = @"
#!/bin/bash
set -e

echo "=== Проверка и установка зависимостей ==="

# Обновление пакетов (для Ubuntu/Debian)
if command -v apt-get &> /dev/null; then
    echo "Обновление пакетов (apt-get)..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv git postgresql postgresql-contrib ffmpeg
elif command -v yum &> /dev/null; then
    echo "Обновление пакетов (yum)..."
    sudo yum install -y python3 python3-pip git postgresql postgresql-server ffmpeg
elif command -v dnf &> /dev/null; then
    echo "Обновление пакетов (dnf)..."
    sudo dnf install -y python3 python3-pip git postgresql postgresql-server ffmpeg
else
    echo "⚠️ Не удалось определить менеджер пакетов. Установите вручную:"
    echo "   - Python 3.11+"
    echo "   - pip"
    echo "   - Git"
    echo "   - PostgreSQL"
    echo "   - FFmpeg"
fi

# Проверка версий
echo ""
echo "Проверка установленных версий:"
python3 --version || echo "❌ Python3 не установлен"
pip3 --version || echo "❌ pip3 не установлен"
git --version || echo "❌ Git не установлен"
psql --version || echo "❌ PostgreSQL не установлен"
ffmpeg -version | head -n 1 || echo "❌ FFmpeg не установлен"

echo ""
echo "=== Настройка PostgreSQL ==="
echo "Создайте базу данных вручную:"
echo "  sudo -u postgres psql"
echo "  CREATE DATABASE english_lessons;"
echo "  CREATE USER your_user WITH PASSWORD 'your_password';"
echo "  GRANT ALL PRIVILEGES ON DATABASE english_lessons TO your_user;"
echo "  \q"

echo ""
echo "✅ Базовая настройка завершена!"
echo ""
echo "Следующие шаги:"
echo "1. Настройте PostgreSQL (создайте БД и пользователя)"
echo "2. Запустите деплой: .\deploy_to_server.ps1"
"@

# Сохраняем скрипт во временный файл с правильной кодировкой (UTF-8 без BOM, LF)
$tempScriptPath = Join-Path $env:TEMP "setup_server_script_$(Get-Date -Format 'yyyyMMddHHmmss').sh"
# Конвертируем CRLF в LF и сохраняем в UTF-8 без BOM
$setupScriptUnix = $setupScript -replace "`r`n", "`n"
[System.IO.File]::WriteAllText($tempScriptPath, $setupScriptUnix, [System.Text.UTF8Encoding]::new($false))

# Копируем скрипт на сервер и выполняем
Write-Host "Выполнение скрипта настройки на сервере..." -ForegroundColor Yellow
& "C:\Windows\System32\OpenSSH\scp.exe" -F $SSHConfig $tempScriptPath "${ServerHost}:~/setup_server_script.sh" | Out-Null
$setupOutput = & "C:\Windows\System32\OpenSSH\ssh.exe" -F $SSHConfig $ServerHost "chmod +x ~/setup_server_script.sh && bash ~/setup_server_script.sh && rm ~/setup_server_script.sh"
Write-Host $setupOutput

# Удаляем временный файл
Remove-Item -Force $tempScriptPath -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "✅ Настройка завершена!" -ForegroundColor Green

