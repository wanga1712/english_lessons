-- Создание базы данных для English Lessons App
-- Выполните этот скрипт от имени суперпользователя PostgreSQL

-- Создание базы данных (если не существует)
SELECT 'CREATE DATABASE english_lessons'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'english_lessons')\gexec

-- Подключение к созданной базе данных
\c english_lessons

-- Включение расширения для UUID (если нужно в будущем)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Примечание: Таблицы будут созданы автоматически через Django миграции
-- Выполните: python manage.py migrate

