# Инструкция: Залить на Git и развернуть на сервере

## Шаг 1: Инициализация Git и загрузка на GitHub/GitLab

### 1.1. Проверка текущего состояния Git

```powershell
cd C:\Users\wangr\PycharmProjects\pythonProject94
git status
```

### 1.2. Если Git еще не инициализирован:

```powershell
# Инициализация Git
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: English Lessons App with Adventure Map"
```

### 1.3. Создание репозитория на GitHub

1. Зайдите на https://github.com
2. Нажмите "New repository"
3. Название: `english-lessons-app` (или любое другое)
4. **НЕ** добавляйте README, .gitignore, license (они уже есть)
5. Нажмите "Create repository"

### 1.4. Подключение к удаленному репозиторию и загрузка

```powershell
# Добавьте remote (замените YOUR_USERNAME на ваш GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/english-lessons-app.git

# Или если используете SSH:
# git remote add origin git@github.com:YOUR_USERNAME/english-lessons-app.git

# Переименуйте ветку в main (если нужно)
git branch -M main

# Загрузите код на GitHub
git push -u origin main
```

### 1.5. Если репозиторий уже существует и нужно обновить:

```powershell
git add .
git commit -m "Update: Added deployment scripts and improved adventure map"
git push origin main
```

## Шаг 2: Развертывание на сервер

### 2.1. Быстрый деплой через Git скрипт:

```powershell
# Укажите URL вашего репозитория
.\deploy_via_git.ps1 -GitRepo "https://github.com/YOUR_USERNAME/english-lessons-app.git"
```

### 2.2. Или вручную на сервере:

```powershell
# Подключитесь к серверу
& "C:\Windows\System32\OpenSSH\ssh.exe" -F "$env:USERPROFILE\.ssh\config" nyx
```

На сервере выполните:

```bash
# Перейдите в домашнюю директорию
cd ~

# Клонируйте репозиторий
git clone https://github.com/YOUR_USERNAME/english-lessons-app.git english_lessons
cd english_lessons

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install --upgrade pip
pip install -r requirements.txt

# Создайте .env файл
nano .env
# (вставьте настройки из локального .env файла)

# Примените миграции
python manage.py migrate

# Создайте суперпользователя
python manage.py createsuperuser

# Соберите статические файлы
python manage.py collectstatic --noinput
```

## Шаг 3: Подключение Cursor к серверу (чтобы AI работал напрямую)

### 3.1. Установка расширения Remote SSH

1. Откройте Cursor
2. Нажмите `Ctrl+Shift+X` (или `F1` → "Extensions: Install Extensions")
3. Найдите: **"Remote - SSH"**
4. Установите расширение от Microsoft

### 3.2. Подключение к серверу

1. Нажмите `F1` (или `Ctrl+Shift+P`)
2. Введите: `Remote-SSH: Connect to Host`
3. Выберите `nyx` из списка (или введите: `ssh -F ~/.ssh/config nyx`)
4. Дождитесь подключения (может потребоваться ввести пароль или подтвердить ключ)

### 3.3. Открытие проекта на сервере

1. После подключения нажмите `File > Open Folder` (или `Ctrl+K Ctrl+O`)
2. Введите путь: `/home/wanga/english_lessons`
   - Или: `~/english_lessons`
3. Нажмите OK

### 3.4. Проверка подключения

- В левом нижнем углу Cursor должно быть написано: `SSH: nyx`
- Терминал должен работать на сервере (проверьте: `hostname` должен показать имя сервера)
- Файлы проекта должны быть видны в Explorer

### 3.5. Готово!

Теперь я (AI) смогу:
- ✅ Читать файлы на сервере
- ✅ Редактировать код напрямую на сервере
- ✅ Выполнять команды на сервере
- ✅ Видеть структуру проекта

## Шаг 4: Обновление проекта на сервере

### Через Git (рекомендуется):

```bash
# На сервере (через терминал Cursor или SSH)
cd ~/english_lessons
git pull origin main

# Обновите зависимости (если requirements.txt изменился)
source venv/bin/activate
pip install -r requirements.txt

# Примените миграции (если есть новые)
python manage.py migrate

# Перезапустите сервер (если используете systemd)
sudo systemctl restart english_lessons
```

### Или через скрипт:

```powershell
# С локальной машины
.\deploy_via_git.ps1 -GitRepo "https://github.com/YOUR_USERNAME/english-lessons-app.git"
```

## Полезные команды

### Проверка статуса Git:

```powershell
git status
git log --oneline -5
```

### Просмотр изменений перед коммитом:

```powershell
git diff
```

### Отправка изменений:

```powershell
git add .
git commit -m "Описание изменений"
git push origin main
```

### На сервере - обновление:

```bash
cd ~/english_lessons
git pull
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

## Troubleshooting

### Проблема: "git: command not found"
- Установите Git: https://git-scm.com/download/win

### Проблема: "Permission denied" при push
- Настройте SSH ключи для GitHub: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### Проблема: Remote SSH не подключается
- Проверьте SSH: `ssh -F ~/.ssh/config nyx`
- Убедитесь, что расширение Remote SSH установлено
- Перезапустите Cursor

### Проблема: Не вижу файлы на сервере
- Проверьте путь: `ls ~/english_lessons`
- Убедитесь, что открыли правильную папку в Cursor

