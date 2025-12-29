# ✅ Настройка сервера завершена!

## Что сделано:

1. ✅ **CUDA удален** - установлен CPU-only PyTorch
2. ✅ **Видео удаляются после обработки** - добавлено в `video_processor.py`
3. ✅ **Пути для видео на сервере** - `/var/www/english_lessons/uploads/videos`
4. ✅ **Проект обновлен** на сервере через Git

## Следующие шаги:

### 1. Создайте .env файл на сервере:

```powershell
# Замените YOUR_OPENROUTER_KEY на ваш ключ
.\setup_server_env.ps1 -OpenRouterKey "YOUR_OPENROUTER_KEY" -ServerDomain "your-domain.com" -PostgresUser "postgres" -PostgresPassword "your_password"
```

Или вручную на сервере:

```bash
cd ~/english_lessons/english_lessons
nano .env
```

Вставьте (замените значения):
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-ip

DB_NAME=english_lessons
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
USE_POSTGRES=True

OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_MODEL=openai/gpt-4o-mini

WATCHED_VIDEO_DIRECTORY=/var/www/english_lessons/uploads/videos
TEMP_AUDIO_DIRECTORY=/tmp/english_lessons_audio

WHISPER_MODEL=base
FFMPEG_BINARY=ffmpeg
```

### 2. Примените миграции:

```bash
cd ~/english_lessons/english_lessons
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
```

### 3. Подключите Cursor через Remote SSH:

1. **В Cursor нажмите `F1`**
2. **Введите:** `Remote-SSH: Connect to Host...`
3. **Выберите `nyx`** из списка (или введите `ssh -F ~/.ssh/config nyx`)
4. **После подключения:** `File > Open Folder` → `~/english_lessons/english_lessons`

**Если список пустой:**
- Проверьте SSH config: `cat ~/.ssh/config`
- Убедитесь, что хост `nyx` там есть
- Попробуйте: `F1` → `Remote-SSH: Connect to Host...` → введите `wanga@nyx`

### 4. Запустите сервер:

```bash
cd ~/english_lessons/english_lessons
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

## Важные изменения:

- ✅ **Видео удаляются автоматически** после успешной обработки
- ✅ **CPU-only PyTorch** - нет CUDA зависимостей
- ✅ **Пути на сервере:** `/var/www/english_lessons/uploads/videos`
- ✅ **База данных:** использует существующую `english_lessons` в PostgreSQL

## Проверка:

```bash
# Проверьте, что CUDA нет
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
# Должно быть: CUDA available: False

# Проверьте директории
ls -la /var/www/english_lessons/uploads/videos
```

