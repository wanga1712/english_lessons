# Скрипт для загрузки проекта на GitHub
# Использование: .\PUSH_TO_GIT.ps1 -GitHubUsername "your-username"

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername,
    
    [string]$RepoName = "english-lessons-app"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Загрузка проекта на GitHub ===" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "C:\Users\wangr\PycharmProjects\pythonProject94"
Set-Location $projectRoot

# Проверка Git
Write-Host "Проверка Git..." -ForegroundColor Yellow
$gitStatus = git status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git не инициализирован!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Git репозиторий найден" -ForegroundColor Green
Write-Host ""

# Проверка remote
Write-Host "Проверка remote..." -ForegroundColor Yellow
$remoteUrl = "https://github.com/$GitHubUsername/$RepoName.git"
$existingRemote = git remote get-url origin 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "⚠️ Remote уже настроен: $existingRemote" -ForegroundColor Yellow
    $useExisting = Read-Host "Использовать существующий remote? (y/n)"
    if ($useExisting -ne "y") {
        git remote set-url origin $remoteUrl
        Write-Host "✅ Remote обновлен: $remoteUrl" -ForegroundColor Green
    }
} else {
    Write-Host "Добавление remote..." -ForegroundColor Yellow
    git remote add origin $remoteUrl
    Write-Host "✅ Remote добавлен: $remoteUrl" -ForegroundColor Green
}
Write-Host ""

# Проверка коммитов
Write-Host "Проверка коммитов..." -ForegroundColor Yellow
$commitCount = (git log --oneline | Measure-Object -Line).Lines
if ($commitCount -eq 0) {
    Write-Host "⚠️ Нет коммитов! Создаю начальный коммит..." -ForegroundColor Yellow
    git add .
    git commit -m "Initial commit: English Lessons App"
}
Write-Host "✅ Найдено коммитов: $commitCount" -ForegroundColor Green
Write-Host ""

# Переименование ветки в main (если нужно)
Write-Host "Проверка ветки..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    Write-Host "Переименование ветки $currentBranch → main..." -ForegroundColor Yellow
    git branch -M main
    Write-Host "✅ Ветка переименована в main" -ForegroundColor Green
}
Write-Host ""

# Push на GitHub
Write-Host "Загрузка на GitHub..." -ForegroundColor Yellow
Write-Host "URL: $remoteUrl" -ForegroundColor Cyan
Write-Host ""

$pushResult = git push -u origin main 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Проект успешно загружен на GitHub!" -ForegroundColor Green
    Write-Host "Репозиторий: https://github.com/$GitHubUsername/$RepoName" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Ошибка при загрузке:" -ForegroundColor Red
    Write-Host $pushResult -ForegroundColor Red
    Write-Host ""
    Write-Host "Возможные причины:" -ForegroundColor Yellow
    Write-Host "1. Репозиторий не создан на GitHub" -ForegroundColor White
    Write-Host "2. Неправильный username или название репозитория" -ForegroundColor White
    Write-Host "3. Нет прав доступа (настройте SSH ключи или используйте Personal Access Token)" -ForegroundColor White
    Write-Host ""
    Write-Host "Создайте репозиторий здесь: https://github.com/new" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "✅ Готово!" -ForegroundColor Green

