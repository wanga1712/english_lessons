"""
Management команда для мониторинга папки с видеофайлами
"""
import time
import logging
from django.core.management.base import BaseCommand
from lessons.services.video_watcher import VideoWatcher

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Мониторинг папки с видеофайлами и автоматическая обработка новых файлов'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--process-existing',
            action='store_true',
            help='Обработать уже существующие файлы в папке',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Запуск мониторинга папки с видео...'))
        
        watcher = VideoWatcher()
        
        # Обработка существующих файлов, если указан флаг
        if options['process_existing']:
            self.stdout.write('Обработка существующих файлов...')
            watcher.process_existing_files()
        
        # Запуск мониторинга
        watcher.start()
        
        try:
            self.stdout.write(self.style.SUCCESS('Мониторинг запущен. Нажмите Ctrl+C для остановки.'))
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nОстановка мониторинга...'))
            watcher.stop()
            self.stdout.write(self.style.SUCCESS('Мониторинг остановлен.'))

