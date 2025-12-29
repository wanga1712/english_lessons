# 🚀 Финальная настройка сервера

## ✅ Что уже сделано:

1. ✅ CUDA удален - установлен CPU-only PyTorch
2. ✅ Видео удаляются после обработки
3. ✅ Пути для видео настроены: `/var/www/english_lessons/uploads/videos`
4. ✅ Проект обновлен на сервере

## 📝 Что нужно сделать:

### 1. Создайте .env файл на сервере

**Вариант A: Через скрипт (проще):**
```powershell
.\setup_server_env.ps1 -OpenRouterKey "ваш-ключ-openrouter" -ServerDomain "ваш-домен-или-ip" -PostgresUser "postgres" -PostgresPassword "ваш-пароль"
```

**Вариант B: Вручную на сервере:**
```bash
cd ~/english_lessons/english_lessons
nano .env
```

Вставьте (замените значения):
```env
SECRET_KEY=сгенерируйте-через-python-manage.py-shell
DEBUG=False
ALLOWED_HOSTS=ваш-домен.com,ваш-ip

DB_NAME=english_lessons
DB_USER=postgres
DB_PASSWORD=ваш-пароль-postgres
DB_HOST=localhost
DB_PORT=5432
USE_POSTGRES=True

OPENROUTER_API_KEY=ваш-ключ-openrouter
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

**Шаг 1:** В Cursor нажмите `F1` (или `Ctrl+Shift+P`)

**Шаг 2:** Введите: `Remote-SSH: Connect to Host...`

**Шаг 3:** 
- Если видите список - выберите `nyx`
- Если список пустой - введите: `ssh -F ~/.ssh/config nyx`
- Или введите: `wanga@nyx` (если знаете user@host)

**Шаг 4:** После подключения:
- `File > Open Folder` (или `Ctrl+K Ctrl+O`)
- Введите: `~/english_lessons/english_lessons`
- Нажмите OK

**Готово!** Теперь я (AI) смогу работать с проектом напрямую на сервере! 🎉

### 4. Запустите сервер:

```bash
cd ~/english_lessons/english_lessons
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

## 🔍 Проверка:

```bash
# Проверьте CUDA (должно быть False)
python -c "import torch; print('CUDA:', torch.cuda.is_available())"

# Проверьте директории
ls -la /var/www/english_lessons/uploads/videos
```

## 📌 Важно:

- **Видео удаляются автоматически** после обработки
- **База данных:** использует существующую `english_lessons` в PostgreSQL
- **Пути:** видео сохраняются в `/var/www/english_lessons/uploads/videos`

