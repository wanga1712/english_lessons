@echo off
echo Запуск Django сервера для доступа извне...
echo.
echo Сервер будет доступен по адресам:
echo   - http://127.0.0.1:8000/ (локально)
echo   - http://localhost:8000/ (локально)
echo   - http://[ваш-ip]:8000/ (из сети)
echo.
echo Для остановки нажмите Ctrl+C
echo.
cd /d %~dp0
.\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
pause

