"""
Сервис для мониторинга папки с видеофайлами
"""
import os
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.conf import settings
from lessons.models import VideoFile

logger = logging.getLogger(__name__)


class VideoFileHandler(FileSystemEventHandler):
    """Обработчик событий файловой системы для видеофайлов"""
    
    # Поддерживаемые форматы видео
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}
    
    def on_created(self, event):
        """Обработка события создания файла"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in self.VIDEO_EXTENSIONS:
            logger.info(f'Обнаружен новый видеофайл: {file_path}')
            self._process_video_file(file_path)
    
    def _process_video_file(self, file_path):
        """
        Обработка нового видеофайла
        
        Args:
            file_path: Путь к видеофайлу
        """
        try:
            # Проверяем, существует ли файл (иногда событие срабатывает до полной записи)
            if not os.path.exists(file_path):
                logger.warning(f'Файл {file_path} ещё не существует, пропускаем')
                return
            
            # Проверяем размер файла (должен быть больше 0)
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                logger.warning(f'Файл {file_path} пустой, пропускаем')
                return
            
            # Проверяем, не обрабатывается ли уже этот файл
            file_path_normalized = os.path.normpath(file_path)
            existing_video = VideoFile.objects.filter(file_path=file_path_normalized).first()
            
            if existing_video:
                logger.info(f'Видеофайл {file_path} уже существует в БД, пропускаем')
                return
            
            # Создаём запись в БД (без немедленной обработки)
            # Используем дату создания файла на диске, а не текущую дату
            from django.utils import timezone
            from datetime import datetime
            
            file_name = os.path.basename(file_path)
            # Получаем дату создания файла на диске
            file_creation_time = os.path.getctime(file_path)
            file_creation_datetime = timezone.make_aware(
                datetime.fromtimestamp(file_creation_time)
            )
            
            # Создаём объект без сохранения, чтобы установить created_at
            video_file = VideoFile(
                file_path=file_path_normalized,
                file_name=file_name,
                file_size=file_size,
                status='pending'
            )
            # Устанавливаем дату создания файла вручную
            video_file.created_at = file_creation_datetime
            video_file.save()
            
            logger.info(f'Создана запись VideoFile {video_file.id} для {file_path}')
            
        except Exception as e:
            logger.error(f'Ошибка обработки видеофайла {file_path}: {str(e)}', exc_info=True)


class VideoWatcher:
    """Класс для мониторинга папки с видео"""
    
    def __init__(self, directory=None):
        """
        Инициализация watcher
        
        Args:
            directory: Путь к папке для мониторинга (по умолчанию из settings)
        """
        self.directory = directory or settings.WATCHED_VIDEO_DIRECTORY
        self.observer = None
        self.handler = VideoFileHandler()
    
    def start(self):
        """Запуск мониторинга"""
        if not os.path.exists(self.directory):
            logger.warning(f'Папка {self.directory} не существует, создаём её')
            os.makedirs(self.directory, exist_ok=True)
        
        if not os.path.isdir(self.directory):
            raise ValueError(f'{self.directory} не является папкой')
        
        self.observer = Observer()
        # Рекурсивный обход подпапок с видео
        self.observer.schedule(self.handler, self.directory, recursive=True)
        self.observer.start()
        
        logger.info(f'Запущен мониторинг папки: {self.directory}')
    
    def stop(self):
        """Остановка мониторинга"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info('Мониторинг остановлен')
    
    def process_existing_files(self):
        """
        Обработка уже существующих файлов в папке
        (для первоначальной загрузки)
        """
        logger.info(f'Обработка существующих файлов в {self.directory}')
        
        video_extensions = VideoFileHandler.VIDEO_EXTENSIONS
        
        for root, _, files in os.walk(self.directory):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                file_ext = Path(file_path).suffix.lower()
                if file_ext in video_extensions:
                    file_path_normalized = os.path.normpath(file_path)

                    # Проверяем, не зарегистрирован ли уже файл
                    existing_video = VideoFile.objects.filter(
                        file_path=file_path_normalized
                    ).first()

                    if not existing_video:
                        logger.info(f'Регистрация существующего файла: {file_path}')
                        self.handler._process_video_file(file_path)

