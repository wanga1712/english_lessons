# Скрипт для запуска Django сервера разработки
# Использование: .\runserver.ps1

Write-Host "=== Запуск Django сервера разработки ===" -ForegroundColor Cyan
Write-Host ""

# Активация виртуального окружения
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "Активация виртуального окружения..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
} else {
    Write-Host "Ошибка: виртуальное окружение не найдено!" -ForegroundColor Red
    Write-Host "Создайте виртуальное окружение: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Проверка установки Django
Write-Host "Проверка установки Django..." -ForegroundColor Yellow
$djangoInstalled = & ".\venv\Scripts\python.exe" -m pip show Django 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Django не установлен. Установка зависимостей..." -ForegroundColor Yellow
    & ".\venv\Scripts\python.exe" -m pip install -r requirements.txt
}

Write-Host ""
Write-Host "Запуск сервера разработки..." -ForegroundColor Green
Write-Host ""

# Запуск Django сервера
& ".\venv\Scripts\python.exe" manage.py runserver

