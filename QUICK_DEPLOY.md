# Быстрая инструкция по деплою

## ⚠️ Важно!

**PowerShell скрипты (`*.ps1`) работают ТОЛЬКО на Windows!**

На сервере (Linux) они не работают. Скрипты предназначены для запуска с вашей Windows машины, они подключаются к серверу через SSH.

## Шаг 1: Запуск с Windows машины

Откройте PowerShell **в директории проекта**:

```powershell
cd C:\Users\wangr\PycharmProjects\pythonProject94
.\setup_server.ps1
```

## Шаг 2: Что делает setup_server.ps1?

Этот скрипт:
- Подключается к серверу через SSH
- Устанавливает необходимые пакеты (Python, PostgreSQL, FFmpeg и т.д.)

## Шаг 3: Деплой проекта

После настройки сервера:

```powershell
cd C:\Users\wangr\PycharmProjects\pythonProject94
.\deploy_to_server.ps1
```

## Альтернатива: Ручная настройка на сервере

Если хотите настроить сервер вручную, подключитесь к нему:

```powershell
& "C:\Windows\System32\OpenSSH\ssh.exe" -F "$env:USERPROFILE\.ssh\config" nyx
```

И выполните на сервере (Linux команды):

```bash
# Обновление пакетов (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git postgresql postgresql-contrib ffmpeg

# Или для CentOS/RHEL
sudo yum install -y python3 python3-pip git postgresql postgresql-server ffmpeg

# Проверка версий
python3 --version
pip3 --version
git --version
psql --version
ffmpeg -version
```

## Что дальше?

После настройки сервера запустите деплой:

```powershell
cd C:\Users\wangr\PycharmProjects\pythonProject94
.\deploy_to_server.ps1
```

