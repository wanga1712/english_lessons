@echo off
echo Запуск Django сервера (только локально)...
echo.
echo Сервер будет доступен по адресам:
echo   - http://127.0.0.1:8000/
echo   - http://localhost:8000/
echo.
echo Для остановки нажмите Ctrl+C
echo.
cd /d %~dp0
.\venv\Scripts\python.exe manage.py runserver
pause

