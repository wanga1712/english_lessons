# Как работать с проектом на сервере через Cursor

## Вариант 1: Remote SSH в Cursor (Рекомендуется)

Cursor поддерживает работу с удаленными проектами через SSH, как VS Code.

### Настройка Remote SSH:

1. **Установите расширение Remote SSH** (если еще не установлено):
   - Откройте Cursor
   - Перейдите в Extensions (Ctrl+Shift+X)
   - Найдите "Remote - SSH" и установите

2. **Подключитесь к серверу**:
   - Нажмите `F1` или `Ctrl+Shift+P`
   - Введите: `Remote-SSH: Connect to Host`
   - Выберите `nyx` (из вашего SSH config)
   - Или введите: `ssh -F ~/.ssh/config nyx`

3. **Откройте папку проекта на сервере**:
   - После подключения нажмите `File > Open Folder`
   - Введите путь: `/home/wanga/english_lessons/english_lessons`
   - Или: `~/english_lessons/english_lessons`

4. **Готово!** Теперь вы можете работать с проектом на сервере, и я (AI) смогу:
   - Читать файлы на сервере
   - Редактировать код
   - Выполнять команды на сервере
   - Видеть структуру проекта

### Преимущества:
- ✅ Полный доступ к файлам на сервере
- ✅ Я могу работать с проектом напрямую
- ✅ Автоматическая синхронизация
- ✅ Терминал работает на сервере

## Вариант 2: Локальная работа + синхронизация через Git

1. **Работайте локально** в Cursor
2. **Коммитьте изменения** в Git
3. **Деплой через Git скрипт**:
   ```powershell
   .\deploy_via_git.ps1
   ```

### Преимущества:
- ✅ Быстрая работа локально
- ✅ Контроль версий через Git
- ✅ Легкий откат изменений

## Вариант 3: Синхронизация файлов

Используйте скрипт для синхронизации:

```powershell
# Отправка файлов на сервер
.\sync_files.ps1 -Direction push

# Загрузка файлов с сервера
.\sync_files.ps1 -Direction pull
```

## Рекомендуемый workflow:

### Для разработки:
1. Используйте **Remote SSH** в Cursor для работы напрямую на сервере
2. Я смогу видеть и редактировать файлы на сервере
3. Изменения применяются сразу

### Для production:
1. Работайте локально
2. Коммитьте в Git
3. Деплойте через `.\deploy_via_git.ps1`

## Быстрый старт с Remote SSH:

```powershell
# 1. Убедитесь, что SSH config настроен
cat ~/.ssh/config

# 2. В Cursor: F1 -> Remote-SSH: Connect to Host -> nyx

# 3. Откройте папку: ~/english_lessons/english_lessons

# 4. Готово! Теперь я могу работать с проектом на сервере
```

## Полезные команды в Remote SSH:

```bash
# На сервере через терминал Cursor:
cd ~/english_lessons/english_lessons
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Или через скрипт:
.\run_on_server.ps1 "cd ~/english_lessons/english_lessons && source venv/bin/activate && python manage.py runserver"
```

## Настройка Git на сервере (если нужно):

```bash
# На сервере:
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Если используете SSH ключи:
ssh-keygen -t ed25519 -C "your.email@example.com"
cat ~/.ssh/id_ed25519.pub
# Добавьте этот ключ в GitHub/GitLab
```

## Troubleshooting:

### Проблема: Cursor не подключается к серверу
- Проверьте SSH подключение: `ssh -F ~/.ssh/config nyx`
- Убедитесь, что расширение Remote SSH установлено
- Проверьте права доступа к SSH ключам

### Проблема: Не вижу файлы на сервере
- Убедитесь, что открыли правильную папку
- Проверьте путь: `ls ~/english_lessons/english_lessons`

### Проблема: Python не найден
- Активируйте виртуальное окружение: `source venv/bin/activate`
- Или используйте полный путь: `~/english_lessons/english_lessons/venv/bin/python`

