# 🚀 Быстрый старт: Git → Сервер → Cursor Remote SSH

## Шаг 1: Залить проект на Git

```powershell
cd C:\Users\wangr\PycharmProjects\pythonProject94

# Добавить все файлы
git add .

# Создать коммит
git commit -m "English Lessons App: Adventure Map with Phaser, deployment scripts"

# Проверить, есть ли remote (если нет - добавить)
git remote -v

# Если remote нет, добавьте (замените YOUR_USERNAME):
git remote add origin https://github.com/YOUR_USERNAME/english-lessons-app.git

# Переименовать ветку в main (если нужно)
git branch -M main

# Загрузить на GitHub
git push -u origin main
```

**Если репозитория на GitHub еще нет:**
1. Зайдите на https://github.com
2. Нажмите "New repository"
3. Название: `english-lessons-app`
4. **НЕ** добавляйте README, .gitignore (они уже есть)
5. Создайте репозиторий
6. Выполните команды выше

## Шаг 2: Развернуть на сервер

```powershell
# Вариант A: Через скрипт (замените YOUR_USERNAME)
.\deploy_via_git.ps1 -GitRepo "https://github.com/YOUR_USERNAME/english-lessons-app.git"

# Вариант B: Вручную на сервере
& "C:\Windows\System32\OpenSSH\ssh.exe" -F "$env:USERPROFILE\.ssh\config" nyx
```

**На сервере выполните:**
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/english-lessons-app.git english_lessons
cd english_lessons
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Создайте .env файл (скопируйте с локальной машины)
nano .env

# Примените миграции
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## Шаг 3: Подключить Cursor к серверу (чтобы AI работал напрямую)

### 3.1. Установите расширение Remote SSH:
1. Откройте Cursor
2. `Ctrl+Shift+X` → найдите **"Remote - SSH"** → установите

### 3.2. Подключитесь к серверу:
1. `F1` (или `Ctrl+Shift+P`)
2. Введите: `Remote-SSH: Connect to Host`
3. Выберите `nyx`

### 3.3. Откройте проект:
1. `File > Open Folder` (или `Ctrl+K Ctrl+O`)
2. Введите: `~/english_lessons`
3. Нажмите OK

### 3.4. Готово! ✅
Теперь я (AI) смогу работать с проектом напрямую на сервере!

## Обновление проекта на сервере:

```bash
# На сервере (через терминал Cursor)
cd ~/english_lessons
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

## Все команды одной строкой:

```powershell
# 1. Git
cd C:\Users\wangr\PycharmProjects\pythonProject94; git add .; git commit -m "Deploy"; git push origin main

# 2. Деплой
.\deploy_via_git.ps1 -GitRepo "https://github.com/YOUR_USERNAME/english-lessons-app.git"

# 3. В Cursor: F1 → Remote-SSH: Connect to Host → nyx → Open Folder → ~/english_lessons
```

