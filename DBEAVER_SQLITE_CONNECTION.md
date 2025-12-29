# Подключение к SQLite в DBeaver

## Текущая ситуация
- Django использует SQLite (файл: `db.sqlite3`)
- PostgreSQL недоступен (таймаут подключения)
- В SQLite: 0 уроков, 0 видео

## Как подключиться к SQLite в DBeaver:

1. Откройте DBeaver
2. Создайте новое подключение:
   - Database → New Database Connection
   - Выберите **SQLite**
3. В настройках подключения:
   - **Path**: `C:\Users\wangr\PycharmProjects\pythonProject94\db.sqlite3`
   - Или нажмите "Browse" и выберите файл `db.sqlite3` в корне проекта
4. Нажмите "Test Connection" → должно быть "Connected"
5. Нажмите "Finish"

## Таблицы в базе:
- `lessons_lesson` - уроки
- `lessons_videofile` - видео файлы
- `lessons_exercisecard` - карточки упражнений
- `lessons_userprogress` - прогресс пользователей
- И другие...

## Проверка данных:
```sql
SELECT COUNT(*) FROM lessons_lesson;
SELECT COUNT(*) FROM lessons_videofile;
SELECT * FROM lessons_lesson LIMIT 10;
```

