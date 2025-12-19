# PowerShell скрипт для настройки PostgreSQL базы данных
# Использование: .\setup_database.ps1

Write-Host "=== Настройка PostgreSQL для English Lessons App ===" -ForegroundColor Cyan
Write-Host ""

# Запрос данных для подключения
$dbUser = Read-Host "Введите имя пользователя PostgreSQL (по умолчанию: postgres)"
if ([string]::IsNullOrWhiteSpace($dbUser)) {
    $dbUser = "postgres"
}

$dbPassword = Read-Host "Введите пароль PostgreSQL" -AsSecureString
$dbPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword)
)

$dbHost = Read-Host "Введите хост PostgreSQL (по умолчанию: localhost)"
if ([string]::IsNullOrWhiteSpace($dbHost)) {
    $dbHost = "localhost"
}

$dbPort = Read-Host "Введите порт PostgreSQL (по умолчанию: 5432)"
if ([string]::IsNullOrWhiteSpace($dbPort)) {
    $dbPort = "5432"
}

Write-Host ""
Write-Host "Создание базы данных..." -ForegroundColor Yellow

# Установка переменной окружения для пароля
$env:PGPASSWORD = $dbPasswordPlain

# Создание базы данных
$createDbQuery = "SELECT 'CREATE DATABASE english_lessons' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'english_lessons');"
$result = psql -U $dbUser -h $dbHost -p $dbPort -d postgres -t -c $createDbQuery

if ($result -match "CREATE DATABASE") {
    psql -U $dbUser -h $dbHost -p $dbPort -d postgres -c "CREATE DATABASE english_lessons;" 2>&1 | Out-Null
    Write-Host "✓ База данных 'english_lessons' создана или уже существует" -ForegroundColor Green
} else {
    Write-Host "✓ База данных 'english_lessons' уже существует" -ForegroundColor Green
}

# Проверка подключения
Write-Host ""
Write-Host "Проверка подключения к базе данных..." -ForegroundColor Yellow
$testQuery = "SELECT version();"
$testResult = psql -U $dbUser -h $dbHost -p $dbPort -d english_lessons -t -c $testQuery 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Подключение к базе данных успешно" -ForegroundColor Green
    Write-Host ""
    Write-Host "=== Следующие шаги ===" -ForegroundColor Cyan
    Write-Host "1. Обновите файл .env с данными подключения:" -ForegroundColor White
    Write-Host "   DB_NAME=english_lessons" -ForegroundColor Gray
    Write-Host "   DB_USER=$dbUser" -ForegroundColor Gray
    Write-Host "   DB_PASSWORD=<ваш_пароль>" -ForegroundColor Gray
    Write-Host "   DB_HOST=$dbHost" -ForegroundColor Gray
    Write-Host "   DB_PORT=$dbPort" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Выполните Django миграции:" -ForegroundColor White
    Write-Host "   python manage.py makemigrations" -ForegroundColor Gray
    Write-Host "   python manage.py migrate" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "✗ Ошибка подключения к базе данных" -ForegroundColor Red
    Write-Host $testResult -ForegroundColor Red
    exit 1
}

# Очистка пароля из переменной окружения
Remove-Item Env:\PGPASSWORD

Write-Host "Готово!" -ForegroundColor Green

