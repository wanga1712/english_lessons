# Простой скрипт для создания БД
# Использование: запустите команду ниже в PowerShell

Write-Host "=== Создание базы данных English Lessons ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Выполните следующую команду (замените YOUR_PASSWORD на ваш пароль PostgreSQL):" -ForegroundColor Yellow
Write-Host ""
Write-Host '$env:PGPASSWORD="YOUR_PASSWORD"; psql -U postgres -h localhost -c "CREATE DATABASE english_lessons;"' -ForegroundColor Green
Write-Host ""
Write-Host "Или если база уже существует, выполните проверку:" -ForegroundColor Yellow
Write-Host '$env:PGPASSWORD="YOUR_PASSWORD"; psql -U postgres -h localhost -d english_lessons -c "SELECT version();"' -ForegroundColor Green
Write-Host ""
Write-Host "После успешного создания обновите .env файл и выполните:" -ForegroundColor Cyan
Write-Host "  python manage.py makemigrations" -ForegroundColor Gray
Write-Host "  python manage.py migrate" -ForegroundColor Gray
Write-Host ""

