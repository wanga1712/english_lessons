# Скрипт для выполнения команд на сервере
# Использование: .\run_on_server.ps1 "команда для выполнения"

param(
    [Parameter(Mandatory=$true)]
    [string]$Command,
    
    [string]$ServerHost = "nyx",
    [string]$SSHConfig = "$env:USERPROFILE\.ssh\config"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Выполнение команды на сервере ===" -ForegroundColor Cyan
Write-Host "Сервер: $ServerHost" -ForegroundColor Yellow
Write-Host "Команда: $Command" -ForegroundColor Yellow
Write-Host ""

$output = & "C:\Windows\System32\OpenSSH\ssh.exe" -F $SSHConfig $ServerHost $Command

if ($LASTEXITCODE -eq 0) {
    Write-Host $output
    Write-Host ""
    Write-Host "✅ Команда выполнена успешно" -ForegroundColor Green
} else {
    Write-Host $output
    Write-Host ""
    Write-Host "❌ Ошибка выполнения команды (код: $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}

