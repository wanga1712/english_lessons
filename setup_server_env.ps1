# Скрипт для настройки .env файла на сервере
# Использование: .\setup_server_env.ps1 -OpenRouterKey "your-key"

param(
    [Parameter(Mandatory=$true)]
    [string]$OpenRouterKey,
    
    [string]$ServerHost = "nyx",
    [string]$SSHConfig = "$env:USERPROFILE\.ssh\config",
    [string]$ServerDomain = "",
    [string]$PostgresUser = "postgres",
    [string]$PostgresPassword = ""
)

$ErrorActionPreference = "Stop"

Write-Host "=== Настройка .env файла на сервере ===" -ForegroundColor Cyan
Write-Host ""

# Генерируем SECRET_KEY
Write-Host "Генерация SECRET_KEY..." -ForegroundColor Yellow
$secretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>&1
if ($LASTEXITCODE -ne 0) {
    # Альтернативный способ
    $secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 50 | ForEach-Object {[char]$_})
}

# Если домен не указан, запрашиваем
if ([string]::IsNullOrEmpty($ServerDomain)) {
    $ServerDomain = Read-Host "Введите домен или IP сервера (для ALLOWED_HOSTS)"
}

# Если пароль PostgreSQL не указан, запрашиваем
if ([string]::IsNullOrEmpty($PostgresPassword)) {
    $PostgresPassword = Read-Host "Введите пароль PostgreSQL" -AsSecureString
    $PostgresPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($PostgresPassword))
}

# Создаем .env содержимое
$envContent = @"
# Django Settings
SECRET_KEY=$secretKey
DEBUG=False
ALLOWED_HOSTS=$ServerDomain,localhost,127.0.0.1

# PostgreSQL Database
DB_NAME=english_lessons
DB_USER=$PostgresUser
DB_PASSWORD=$PostgresPassword
DB_HOST=localhost
DB_PORT=5432
USE_POSTGRES=True

# OpenRouter AI
OPENROUTER_API_KEY=$OpenRouterKey
OPENROUTER_MODEL=openai/gpt-4o-mini

# Video Processing (на сервере)
WATCHED_VIDEO_DIRECTORY=/var/www/english_lessons/uploads/videos
TEMP_AUDIO_DIRECTORY=/tmp/english_lessons_audio

# Whisper Model (CPU-only на сервере)
WHISPER_MODEL=base

# FFmpeg
FFMPEG_BINARY=ffmpeg
"@

# Сохраняем во временный файл
$tempEnvFile = Join-Path $env:TEMP "server_env_$(Get-Date -Format 'yyyyMMddHHmmss').env"
$envContent | Out-File -FilePath $tempEnvFile -Encoding UTF8 -NoNewline

# Копируем на сервер
Write-Host "Копирование .env на сервер..." -ForegroundColor Yellow
& "C:\Windows\System32\OpenSSH\scp.exe" -F $SSHConfig $tempEnvFile "${ServerHost}:~/english_lessons/english_lessons/.env" | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ .env файл создан на сервере" -ForegroundColor Green
    
    # Создаем директории для видео
    Write-Host "Создание директорий для видео..." -ForegroundColor Yellow
    & "C:\Windows\System32\OpenSSH\ssh.exe" -F $SSHConfig $ServerHost "sudo mkdir -p /var/www/english_lessons/uploads/videos && sudo chown -R wanga:wanga /var/www/english_lessons && echo '✅ Директории созданы'"
    
    Write-Host ""
    Write-Host "✅ Настройка завершена!" -ForegroundColor Green
} else {
    Write-Host "❌ Ошибка копирования .env файла!" -ForegroundColor Red
    exit 1
}

# Удаляем временный файл
Remove-Item -Force $tempEnvFile -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Следующие шаги:" -ForegroundColor Cyan
Write-Host "1. Примените миграции: ssh -F $SSHConfig $ServerHost 'cd ~/english_lessons/english_lessons && source venv/bin/activate && python manage.py migrate'" -ForegroundColor White
Write-Host "2. Создайте суперпользователя: python manage.py createsuperuser" -ForegroundColor White

