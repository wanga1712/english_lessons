"""
Скрипт для первоначальной настройки проекта
"""
import os
import subprocess
import sys

def check_ffmpeg():
    """Проверка наличия FFmpeg"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print('✓ FFmpeg установлен')
            return True
    except FileNotFoundError:
        pass
    
    print('✗ FFmpeg не найден')
    print('  Установите FFmpeg: https://ffmpeg.org/download.html')
    return False

def check_env_file():
    """Проверка наличия .env файла"""
    if os.path.exists('.env'):
        print('✓ Файл .env существует')
        return True
    else:
        print('✗ Файл .env не найден')
        print('  Создайте файл .env на основе .env.example')
        return False

def create_directories():
    """Создание необходимых директорий"""
    dirs = ['temp_audio', 'videos', 'media']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f'✓ Создана директория: {dir_name}')

def main():
    print('Проверка настроек проекта...\n')
    
    checks = [
        ('FFmpeg', check_ffmpeg),
        ('.env файл', check_env_file),
    ]
    
    all_ok = True
    for name, check_func in checks:
        if not check_func():
            all_ok = False
    
    print('\nСоздание директорий...')
    create_directories()
    
    if all_ok:
        print('\n✓ Проект готов к использованию!')
        print('\nСледующие шаги:')
        print('1. Настройте .env файл с вашими данными')
        print('2. Создайте БД PostgreSQL и укажите в .env')
        print('3. Выполните: python manage.py makemigrations')
        print('4. Выполните: python manage.py migrate')
        print('5. Запустите: python manage.py watch_videos')
    else:
        print('\n✗ Некоторые проверки не пройдены. Исправьте ошибки и повторите.')
        sys.exit(1)

if __name__ == '__main__':
    main()

