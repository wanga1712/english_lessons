# Быстрый старт

## Шаг 1: Настройка окружения

1. Создайте файл `.env` в корне проекта:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=english_lessons
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

OPENROUTER_API_KEY=your-api-key
OPENROUTER_MODEL=openai/gpt-4o-mini

WATCHED_VIDEO_DIRECTORY=D:/english_lessons
TEMP_AUDIO_DIRECTORY=./temp_audio

WHISPER_MODEL=base
```

2. Установите FFmpeg и добавьте в PATH

3. Создайте БД PostgreSQL:
```sql
CREATE DATABASE english_lessons;
```

## Шаг 2: Инициализация проекта

```bash
# Активация виртуального окружения
.\venv\Scripts\activate

# Проверка настроек
python init_project.py

# Применение миграций
python manage.py makemigrations
python manage.py migrate
```

## Шаг 3: Тестирование

### Вариант 1: Автоматический мониторинг

1. Поместите видеофайл в папку `WATCHED_VIDEO_DIRECTORY` (из .env)
2. Запустите watcher:
```bash
python manage.py watch_videos --process-existing
```

### Вариант 2: Ручная обработка через API

1. Запустите сервер:
```bash
python manage.py runserver
```

2. Добавьте видеофайл вручную через админку или создайте запись VideoFile
3. Отправьте POST запрос:
```bash
curl -X POST http://localhost:8000/api/videos/1/process/
```

## Шаг 4: Проверка результатов

1. Откройте админку: http://localhost:8000/admin/
2. Или используйте API:
   - `GET http://localhost:8000/api/lessons/` - список уроков
   - `GET http://localhost:8000/api/lessons/1/` - детали урока с карточками

## Важные замечания

- Первый запуск Whisper загрузит модель (может занять несколько минут)
- Убедитесь, что FFmpeg доступен в PATH
- Проверьте, что папка `WATCHED_VIDEO_DIRECTORY` существует
- OpenRouter API требует интернет-соединение

## Устранение проблем

### Ошибка "FFmpeg not found"
- Установите FFmpeg и добавьте в PATH
- Или укажите полный путь в коде

### Ошибка подключения к БД
- Проверьте настройки в .env
- Убедитесь, что PostgreSQL запущен
- Проверьте права доступа пользователя БД

### Ошибка OpenRouter API
- Проверьте API ключ в .env
- Убедитесь, что есть интернет-соединение
- Проверьте баланс на OpenRouter

### Whisper не загружается
- Убедитесь, что установлен PyTorch
- Проверьте доступное место на диске (модели занимают ~150MB-3GB)
- Попробуйте модель меньшего размера (base вместо small)

