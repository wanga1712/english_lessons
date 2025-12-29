# Инструкция по деплою на сервер

## Подготовка

### 1. Настройка SSH

Убедитесь, что у вас настроен SSH config файл (`~/.ssh/config`) с хостом `nyx`:

```
Host nyx
    HostName your-server-ip-or-domain
    User your-username
    Port 22
    IdentityFile ~/.ssh/your-private-key
```

### 2. Проверка подключения

```powershell
& "C:\Windows\System32\OpenSSH\ssh.exe" -F "$env:USERPROFILE\.ssh\config" nyx "echo 'Connection OK'"
```

## Первоначальная настройка сервера

Запустите скрипт для установки необходимых пакетов:

```powershell
.\setup_server.ps1
```

Этот скрипт установит:
- Python 3.11+
- pip
- Git
- PostgreSQL
- FFmpeg

## Деплой проекта

### Вариант 1: Полный деплой (рекомендуется для первого раза)

```powershell
.\deploy_to_server.ps1
```

Этот скрипт:
1. Создаст архив проекта (исключая ненужные файлы)
2. Скопирует архив на сервер
3. Распакует архив
4. Создаст виртуальное окружение
5. Установит зависимости
6. Применит миграции
7. Соберет статические файлы

### Вариант 2: Деплой без миграций

```powershell
.\deploy_to_server.ps1 -SkipMigrations
```

### Вариант 3: Деплой без резервной копии

```powershell
.\deploy_to_server.ps1 -SkipBackup
```

## Настройка на сервере после деплоя

### 1. Подключитесь к серверу

```powershell
& "C:\Windows\System32\OpenSSH\ssh.exe" -F "$env:USERPROFILE\.ssh\config" nyx
```

### 2. Перейдите в директорию проекта

```bash
cd ~/english_lessons/english_lessons
```

### 3. Создайте файл `.env`

Скопируйте `.env` файл с локальной машины или создайте новый:

```bash
nano .env
```

Пример содержимого:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,server-ip

# PostgreSQL Database
DB_NAME=english_lessons
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# OpenRouter AI
OPENROUTER_API_KEY=your-openrouter-api-key-here
OPENROUTER_MODEL=openai/gpt-4o-mini

# Video Processing
WATCHED_VIDEO_DIRECTORY=/path/to/videos
TEMP_AUDIO_DIRECTORY=./temp_audio

# Whisper Model
WHISPER_MODEL=base

# FFmpeg
FFMPEG_BINARY=ffmpeg
```

### 4. Настройте PostgreSQL

```bash
sudo -u postgres psql
```

В psql:

```sql
CREATE DATABASE english_lessons;
CREATE USER your_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE english_lessons TO your_user;
\q
```

### 5. Примените миграции (если не были применены)

```bash
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
```

### 6. Соберите статические файлы

```bash
python manage.py collectstatic --noinput
```

## Запуск сервера

### Вариант 1: Разработка (вручную)

```bash
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### Вариант 2: Production с Gunicorn

Установите Gunicorn:

```bash
pip install gunicorn
```

Создайте systemd service файл `/etc/systemd/system/english_lessons.service`:

```ini
[Unit]
Description=English Lessons Django App
After=network.target

[Service]
User=your-username
Group=your-group
WorkingDirectory=/home/your-username/english_lessons/english_lessons
Environment="PATH=/home/your-username/english_lessons/english_lessons/venv/bin"
ExecStart=/home/your-username/english_lessons/english_lessons/venv/bin/gunicorn \
    --workers 3 \
    --bind 0.0.0.0:8000 \
    english_lessons.wsgi:application

[Install]
WantedBy=multi-user.target
```

Запустите сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable english_lessons
sudo systemctl start english_lessons
sudo systemctl status english_lessons
```

### Вариант 3: С Nginx (рекомендуется для production)

Установите Nginx:

```bash
sudo apt-get install nginx
```

Создайте конфигурацию `/etc/nginx/sites-available/english_lessons`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /home/your-username/english_lessons/english_lessons/staticfiles/;
    }

    location /media/ {
        alias /home/your-username/english_lessons/english_lessons/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активируйте конфигурацию:

```bash
sudo ln -s /etc/nginx/sites-available/english_lessons /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Синхронизация файлов

### Отправка файлов на сервер

```powershell
.\sync_files.ps1 -Direction push
```

### Загрузка файлов с сервера

```powershell
.\sync_files.ps1 -Direction pull
```

## Использование Git для деплоя (альтернативный способ)

### На сервере:

```bash
cd ~/english_lessons
git clone https://github.com/your-username/english_lessons.git
cd english_lessons
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Обновление через Git:

```bash
cd ~/english_lessons/english_lessons
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart english_lessons
```

## Мониторинг

### Просмотр логов

```bash
# Логи systemd
sudo journalctl -u english_lessons -f

# Логи Django
tail -f ~/english_lessons/english_lessons/logs/*.log
```

### Проверка статуса

```bash
sudo systemctl status english_lessons
ps aux | grep gunicorn
```

## Резервное копирование

### База данных

```bash
pg_dump -U your_user english_lessons > backup_$(date +%Y%m%d).sql
```

### Восстановление

```bash
psql -U your_user english_lessons < backup_20240101.sql
```

## Безопасность

1. **Не храните `.env` в Git** - он уже в `.gitignore`
2. **Используйте сильный SECRET_KEY** в production
3. **Установите DEBUG=False** в production
4. **Настройте ALLOWED_HOSTS** правильно
5. **Используйте HTTPS** через Nginx с Let's Encrypt
6. **Настройте firewall** (ufw):

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Troubleshooting

### Проблема: Не могу подключиться по SSH

- Проверьте SSH config файл
- Проверьте, что сервер доступен: `ping your-server-ip`
- Проверьте ключи SSH

### Проблема: Ошибка при установке зависимостей

- Убедитесь, что Python 3.11+ установлен
- Проверьте, что pip обновлен: `pip install --upgrade pip`

### Проблема: Ошибка подключения к PostgreSQL

- Проверьте, что PostgreSQL запущен: `sudo systemctl status postgresql`
- Проверьте настройки в `.env`
- Проверьте права пользователя БД

### Проблема: Статические файлы не загружаются

- Убедитесь, что `STATIC_ROOT` настроен в `settings.py`
- Запустите `python manage.py collectstatic`
- Проверьте права доступа к директории staticfiles

