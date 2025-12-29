# Скрипт для синхронизации файлов с сервером
# Использование: .\sync_files.ps1 [push|pull]

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("push", "pull")]
    [string]$Direction,
    
    [string]$ServerHost = "nyx",
    [string]$RemotePath = "~/english_lessons/english_lessons",
    [string]$SSHConfig = "$env:USERPROFILE\.ssh\config",
    [string[]]$ExcludePatterns = @("__pycache__", "*.pyc", ".git", "venv", ".env", "db.sqlite3", "temp_audio", "videos", ".cursor", "*.log")
)

$ErrorActionPreference = "Stop"

Write-Host "=== Синхронизация файлов ===" -ForegroundColor Cyan
Write-Host "Направление: $Direction" -ForegroundColor Yellow
Write-Host ""

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($Direction -eq "push") {
    Write-Host "Отправка файлов на сервер..." -ForegroundColor Yellow
    
    # Создаем временный файл с исключениями для rsync
    $excludeFile = Join-Path $env:TEMP "rsync_exclude_$(Get-Date -Format 'yyyyMMddHHmmss').txt"
    $ExcludePatterns | ForEach-Object { Add-Content -Path $excludeFile -Value $_ }
    
    # Используем rsync через SSH (если доступен) или scp
    if (Get-Command rsync -ErrorAction SilentlyContinue) {
        Write-Host "Использование rsync..." -ForegroundColor Yellow
        $rsyncArgs = @(
            "-avz",
            "--exclude-from=$excludeFile",
            "--delete",
            "$projectRoot/",
            "${ServerHost}:${RemotePath}/"
        )
        & rsync $rsyncArgs
    } else {
        Write-Host "rsync не найден, используем scp..." -ForegroundColor Yellow
        Write-Host "⚠️ Для лучшей синхронизации установите rsync или используйте Git" -ForegroundColor Yellow
        
        # Простое копирование через scp (без исключений)
        $filesToSync = Get-ChildItem -Recurse -File | Where-Object {
            $shouldInclude = $true
            foreach ($pattern in $ExcludePatterns) {
                if ($_.FullName -like "*$pattern*") {
                    $shouldInclude = $false
                    break
                }
            }
            return $shouldInclude
        }
        
        foreach ($file in $filesToSync) {
            $relativePath = $file.FullName.Substring($projectRoot.Length + 1).Replace('\', '/')
            $remoteFile = "${ServerHost}:${RemotePath}/${relativePath}"
            Write-Host "Копирование: $relativePath" -ForegroundColor Gray
            & "C:\Windows\System32\OpenSSH\scp.exe" -F $SSHConfig -r $file.FullName $remoteFile | Out-Null
        }
    }
    
    Remove-Item $excludeFile -ErrorAction SilentlyContinue
    Write-Host "✅ Файлы отправлены на сервер" -ForegroundColor Green
    
} elseif ($Direction -eq "pull") {
    Write-Host "Загрузка файлов с сервера..." -ForegroundColor Yellow
    
    # Создаем директорию для загрузки
    $downloadDir = Join-Path $projectRoot "download_from_server"
    if (Test-Path $downloadDir) {
        Remove-Item -Recurse -Force $downloadDir
    }
    New-Item -ItemType Directory -Path $downloadDir | Out-Null
    
    # Загружаем файлы
    & "C:\Windows\System32\OpenSSH\scp.exe" -F $SSHConfig -r "${ServerHost}:${RemotePath}/*" $downloadDir
    
    Write-Host "✅ Файлы загружены с сервера в: $downloadDir" -ForegroundColor Green
    Write-Host "⚠️ Проверьте файлы перед копированием в проект!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Синхронизация завершена!" -ForegroundColor Green

