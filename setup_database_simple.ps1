# Упрощённый скрипт для быстрой настройки БД
# Использование: .\setup_database_simple.ps1 -User postgres -Password your_password

param(
    [string]$User = "postgres",
    [string]$Password = "",
    [string]$DbHost = "localhost",
    [string]$Port = "5432"
)

Write-Host "=== Создание базы данных English Lessons ===" -ForegroundColor Cyan
Write-Host ""

if ([string]::IsNullOrWhiteSpace($Password)) {
    $securePassword = Read-Host "Введите пароль PostgreSQL" -AsSecureString
    $Password = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    )
}

# Установка пароля для psql
$env:PGPASSWORD = $Password

Write-Host "Создание базы данных 'english_lessons'..." -ForegroundColor Yellow

# Проверка существования БД и создание если нужно
$checkDb = psql -U $User -h $DbHost -p $Port -d postgres -t -c "SELECT 1 FROM pg_database WHERE datname = 'english_lessons';" 2>&1

if ($LASTEXITCODE -eq 0 -and [string]::IsNullOrWhiteSpace($checkDb.Trim())) {
    # БД не существует, создаём
    $createResult = psql -U $User -h $DbHost -p $Port -d postgres -c "CREATE DATABASE english_lessons;" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ База данных 'english_lessons' успешно создана" -ForegroundColor Green
    } else {
        Write-Host "✗ Ошибка при создании базы данных:" -ForegroundColor Red
        Write-Host $createResult -ForegroundColor Red
        Remove-Item Env:\PGPASSWORD
        exit 1
    }
} else {
    Write-Host "✓ База данных 'english_lessons' уже существует" -ForegroundColor Green
}

# Проверка подключения
Write-Host ""
Write-Host "Проверка подключения..." -ForegroundColor Yellow
$testResult = psql -U $User -h $DbHost -p $Port -d english_lessons -c "SELECT version();" 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Подключение успешно!" -ForegroundColor Green
    Write-Host ""
    Write-Host "=== Настройка завершена ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Обновите .env файл:" -ForegroundColor White
    Write-Host "DB_NAME=english_lessons" -ForegroundColor Gray
    Write-Host "DB_USER=$User" -ForegroundColor Gray
    Write-Host "DB_PASSWORD=$Password" -ForegroundColor Gray
    Write-Host "DB_HOST=$DbHost" -ForegroundColor Gray
    Write-Host "DB_PORT=$Port" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Затем выполните:" -ForegroundColor White
    Write-Host "  python manage.py makemigrations" -ForegroundColor Yellow
    Write-Host "  python manage.py migrate" -ForegroundColor Yellow
} else {
    Write-Host "✗ Ошибка подключения к базе данных" -ForegroundColor Red
    Write-Host "Проверьте правильность данных подключения" -ForegroundColor Red
}

# Очистка
Remove-Item Env:\PGPASSWORD

