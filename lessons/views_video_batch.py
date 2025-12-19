"""
Views для массовой обработки видео
Размер: ~200 строк
"""
import logging
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from lessons.models import VideoFile, Lesson
from lessons.services.video_processor import VideoProcessor
from lessons.services.video_watcher import VideoWatcher
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class ProcessAllVideosView(View):
    """API endpoint для обработки всех видео по очереди"""
    
    def post(self, request):
        """Обработать все необработанные видео по очереди"""
        try:
            from lessons.services.log_storage import LogStorage
            log_storage = LogStorage.get_instance()
            log_storage.clear()
            
            logger.info('Запрос обработки всех видео')
            watcher = VideoWatcher()
            watcher.process_existing_files()
            
            # Оптимизация: используем select_related для уменьшения запросов
            pending_videos = VideoFile.objects.exclude(status='done').select_related('lesson').order_by('created_at')
            
            if not pending_videos.exists():
                return JsonResponse({
                    'success': True,
                    'message': 'Все видео уже обработаны',
                    'processed_count': 0,
                    'total_count': 0
                })
            
            total_count = pending_videos.count()
            processed_count = 0
            errors = []
            
            processor = VideoProcessor()
            
            # Оптимизация: предзагружаем все уроки одним запросом
            existing_lessons = {l.video_id: l for l in Lesson.objects.filter(
                video_id__in=[v.id for v in pending_videos]
            ).select_related('video')}
            
            for index, video_file in enumerate(pending_videos, 1):
                try:
                    # Оптимизация: используем предзагруженные уроки
                    existing_lesson = existing_lessons.get(video_file.id)
                    if existing_lesson:
                        logger.info(f'Урок для видео {video_file.id} уже существует (урок {existing_lesson.id}), пропускаем')
                        if video_file.status != 'done':
                            video_file.status = 'done'
                            video_file.processing_status = 'done'
                            video_file.processing_message = 'Урок уже существует.'
                            video_file.save()
                        continue
                    
                    # Проверка зависших видео
                    if video_file.status in ('error', 'processing'):
                        if video_file.status == 'processing':
                            if video_file.processed_at:
                                time_diff = timezone.now() - video_file.processed_at
                                if time_diff > timedelta(minutes=10):
                                    logger.warning(f'⚠️ Видео {video_file.id} зависло в обработке более 10 минут, сбрасываем статус')
                                else:
                                    logger.info(f'Видео {video_file.id} ещё обрабатывается, пропускаем')
                                    continue
                        
                        video_file.status = 'pending'
                        video_file.error_message = None
                        video_file.processing_status = 'idle'
                        video_file.processing_message = None
                        video_file.save()
                    
                    video_file.processing_message = f'Обработка видео {index}/{total_count}: {video_file.file_name}'
                    video_file.save(update_fields=['processing_message'])
                    
                    logger.info(f'Обработка видео {index}/{total_count}: {video_file.id} - {video_file.file_name}')
                    import sys
                    sys.stdout.flush()
                    
                    try:
                        lesson = processor.process_video(video_file, force_recreate=False)
                    except Exception as process_error:
                        logger.error(f'❌ ОШИБКА при обработке видео {video_file.id}: {str(process_error)}', exc_info=True)
                        sys.stdout.flush()
                        
                        existing_lesson = existing_lessons.get(video_file.id) or Lesson.objects.filter(video=video_file).first()
                        if existing_lesson:
                            logger.warning(f'⚠️ Урок {existing_lesson.id} был создан несмотря на ошибку')
                            lesson = existing_lesson
                        else:
                            video_file.status = 'error'
                            video_file.processing_status = 'error'
                            video_file.processing_message = f'Ошибка: {str(process_error)}'
                            video_file.error_message = str(process_error)
                            video_file.save()
                            errors.append({
                                'video_id': video_file.id,
                                'file_name': video_file.file_name,
                                'error': str(process_error)
                            })
                            continue
                    
                    if lesson is None:
                        existing_lesson = existing_lessons.get(video_file.id) or Lesson.objects.filter(video=video_file).first()
                        if existing_lesson:
                            logger.info(f'✅ Урок {existing_lesson.id} уже существует для видео {video_file.id}')
                            video_file.status = 'done'
                            video_file.processing_status = 'done'
                            video_file.processing_message = 'Урок уже существует.'
                            video_file.save()
                            processed_count += 1
                        else:
                            logger.error(f'❌ Урок не создан и не существует для видео {video_file.id}')
                        continue
                    
                    cards_count = lesson.cards.count()
                    if cards_count == 0:
                        logger.error(f'❌ КРИТИЧЕСКАЯ ОШИБКА: Урок {lesson.id} создан БЕЗ КАРТОЧЕК!')
                        logger.error(f'   Видео: {video_file.file_name}')
                        logger.error(f'   Урок ID: {lesson.id}')
                        logger.error(f'   Название: {lesson.title}')
                        sys.stdout.flush()
                    
                    processed_count += 1
                    logger.info(f'✅ Видео {video_file.id} успешно обработано, создан урок {lesson.id} с {cards_count} карточками')
                    sys.stdout.flush()
                    
                    video_file.refresh_from_db()
                    if video_file.status != 'done':
                        video_file.status = 'done'
                        video_file.processing_status = 'done'
                        video_file.processing_message = 'Урок успешно создан.'
                        video_file.save()
                    
                except Exception as e:
                    logger.error(f'Ошибка обработки видео {video_file.id}: {str(e)}', exc_info=True)
                    video_file.status = 'error'
                    video_file.processing_status = 'error'
                    video_file.processing_message = f'Ошибка: {str(e)}'
                    video_file.error_message = str(e)
                    video_file.save()
                    errors.append({
                        'video_id': video_file.id,
                        'file_name': video_file.file_name,
                        'error': str(e)
                    })
            
            return JsonResponse({
                'success': True,
                'message': f'Обработано {processed_count} из {total_count} видео',
                'processed_count': processed_count,
                'total_count': total_count,
                'errors': errors if errors else None
            })
            
        except Exception as e:
            logger.error(f'Ошибка обработки всех видео: {str(e)}', exc_info=True)
            return JsonResponse({
                'error': f'Ошибка обработки: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class RecreateAllLessonsView(View):
    """API endpoint для пересоздания всех уроков"""
    
    def post(self, request):
        """Удалить все уроки и пересоздать их из всех видео файлов"""
        try:
            from lessons.services.log_storage import LogStorage
            log_storage = LogStorage.get_instance()
            log_storage.clear()
            
            logger.info('Запрос на пересоздание всех уроков')
            
            lessons_count = Lesson.objects.count()
            Lesson.objects.all().delete()
            logger.info(f'Удалено {lessons_count} уроков из базы данных')
            
            watcher = VideoWatcher()
            watcher.process_existing_files()
            
            all_videos = VideoFile.objects.all().order_by('created_at')
            
            if not all_videos.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Нет видео файлов для обработки',
                    'processed_count': 0,
                    'total_count': 0
                })
            
            total_count = all_videos.count()
            processed_count = 0
            errors = []
            
            processor = VideoProcessor()
            
            for index, video_file in enumerate(all_videos, 1):
                try:
                    video_file.status = 'pending'
                    video_file.error_message = None
                    video_file.processed_at = None
                    video_file.save()
                    
                    video_file.status = 'processing'
                    video_file.save()
                    
                    logger.info(f'Обработка видео {index}/{total_count}: {video_file.id} - {video_file.file_name} (создано: {video_file.created_at})')
                    lesson = processor.process_video(video_file, force_recreate=True)
                    processed_count += 1
                    logger.info(f'Видео {video_file.id} успешно обработано, создан урок {lesson.id}: {lesson.title}')
                    
                except Exception as e:
                    logger.error(f'Ошибка обработки видео {video_file.id}: {str(e)}', exc_info=True)
                    video_file.status = 'error'
                    video_file.error_message = str(e)
                    video_file.save()
                    errors.append({
                        'video_id': video_file.id,
                        'file_name': video_file.file_name,
                        'error': str(e)
                    })
            
            return JsonResponse({
                'success': True,
                'message': f'Пересоздано {processed_count} из {total_count} уроков',
                'processed_count': processed_count,
                'total_count': total_count,
                'deleted_lessons': lessons_count,
                'errors': errors if errors else None
            })
            
        except Exception as e:
            logger.error(f'Ошибка пересоздания всех уроков: {str(e)}', exc_info=True)
            return JsonResponse({
                'error': f'Ошибка пересоздания: {str(e)}'
            }, status=500)

