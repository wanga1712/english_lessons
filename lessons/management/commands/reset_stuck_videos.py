"""
Команда для сброса застрявших видео в статусе processing
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from lessons.models import VideoFile
import os
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Сброс застрявших видео в статусе processing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=2,
            help='Количество часов, после которых видео считается застрявшим (по умолчанию: 2)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать, что будет сделано, без реального изменения',
        )

    def handle(self, *args, **options):
        hours = options['hours']
        dry_run = options['dry_run']
        
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        stuck_videos = VideoFile.objects.filter(
            status='processing',
            created_at__lt=cutoff_time
        )
        
        count = stuck_videos.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('Нет застрявших видео'))
            return
        
        self.stdout.write(f'Найдено застрявших видео: {count}')
        
        for video in stuck_videos:
            file_exists = os.path.exists(video.file_path) if video.file_path else False
            
            if dry_run:
                self.stdout.write(
                    f'  [DRY RUN] ID {video.id}: {video.file_name} '
                    f'(файл: {"существует" if file_exists else "НЕ НАЙДЕН"}, '
                    f'обновлено: {video.updated_at})'
                )
            else:
                if not file_exists:
                    video.status = 'error'
                    video.processing_status = 'error'
                    video.error_message = f'Видеофайл не найден: {video.file_path}'
                    video.processing_message = None
                else:
                    video.status = 'pending'
                    video.processing_status = 'idle'
                    video.processing_message = None
                    video.error_message = None
                
                video.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ ID {video.id}: {video.file_name} -> {video.status}'
                    )
                )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\nСброшено {count} застрявших видео')
            )

