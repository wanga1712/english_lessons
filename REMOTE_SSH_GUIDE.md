# Как подключиться через Remote SSH в Cursor

## Шаг 1: Убедитесь, что расширение установлено
- `Ctrl+Shift+X` → найдите "Remote - SSH" → должно быть "Installed"

## Шаг 2: Подключение к серверу

### Вариант A: Через Command Palette
1. Нажмите `F1` (или `Ctrl+Shift+P`)
2. Введите: `Remote-SSH: Connect to Host...`
3. Должен появиться список хостов из вашего SSH config
4. Выберите `nyx`

### Вариант B: Если список пустой
1. `F1` → `Remote-SSH: Connect to Host...`
2. Введите: `ssh -F ~/.ssh/config nyx`
3. Или введите: `wanga@nyx` (если знаете user@host)

### Вариант C: Через иконку в левом нижнем углу
1. В левом нижнем углу Cursor нажмите на зеленую иконку `><` (или текст "Open Remote Window")
2. Выберите "Connect to Host..."
3. Выберите `nyx` из списка

## Шаг 3: После подключения
1. `File > Open Folder` (или `Ctrl+K Ctrl+O`)
2. Введите: `~/english_lessons/english_lessons`
3. Нажмите OK

## Если не работает:
Проверьте SSH config:
```powershell
cat ~/.ssh/config
```

Должно быть:
```
Host nyx
    HostName ваш-ip-или-домен
    User wanga
    ...
```

