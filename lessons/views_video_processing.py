"""
Views для обработки видео
Размер: ~200 строк
"""
import logging
import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views import View
from django.conf import settings
from lessons.models import VideoFile, Lesson
from lessons.services.video_processor import VideoProcessor

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class ProcessVideoView(View):
    """API endpoint для ручной обработки видео"""
    
    def post(self, request, video_id):
        """Обработать видео вручную"""
        # Убеждаемся, что json импортирован
        import json as json_module
        # #region agent log
        log_path = os.path.join(settings.BASE_DIR, '.cursor', 'debug.log')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json_module.dumps({
                'location': 'views_video_processing.py:20',
                'message': 'ProcessVideoView.post called',
                'data': {'video_id': video_id},
                'timestamp': int(timezone.now().timestamp() * 1000),
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'I'
            }, ensure_ascii=False) + '\n')
        # #endregion
        try:
            video_file = VideoFile.objects.get(id=video_id)
            
            # #region agent log
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({
                    'location': 'views_video_processing.py:25',
                    'message': 'VideoFile found',
                    'data': {
                        'video_id': video_file.id,
                        'file_path': video_file.file_path,
                        'file_path_exists': os.path.exists(video_file.file_path),
                        'status': video_file.status
                    },
                    'timestamp': int(timezone.now().timestamp() * 1000),
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'J'
                }, ensure_ascii=False) + '\n')
            # #endregion
            
            # Проверяем параметр force_recreate из тела запроса
            force_recreate = False
            if request.body:
                try:
                    body_data = json_module.loads(request.body)
                    force_recreate = body_data.get('force_recreate', False)
                except json_module.JSONDecodeError:
                    pass
            
            if video_file.status == 'processing' and not force_recreate:
                return JsonResponse({
                    'error': 'Видео уже обрабатывается'
                }, status=400)
            
            if video_file.status == 'done' and hasattr(video_file, 'lesson') and not force_recreate:
                return JsonResponse({
                    'error': 'Видео уже обработано',
                    'lesson_id': video_file.lesson.id,
                    'message': 'Используйте параметр force_recreate=true для пересоздания урока'
                }, status=400)
            
            video_file.status = 'pending'
            video_file.error_message = None
            video_file.save()
            
            processor = VideoProcessor()
            lesson = processor.process_video(video_file, force_recreate=force_recreate)
            
            return JsonResponse({
                'success': True,
                'message': 'Видео успешно обработано' + (' (урок пересоздан)' if force_recreate else ''),
                'lesson_id': lesson.id,
                'lesson_title': lesson.title,
                'cards_count': lesson.cards.count(),
                'recreated': force_recreate
            })
            
        except VideoFile.DoesNotExist:
            # #region agent log
            import json as json_module
            log_path = os.path.join(settings.BASE_DIR, '.cursor', 'debug.log')
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({
                    'location': 'views_video_processing.py:63',
                    'message': 'VideoFile not found',
                    'data': {'video_id': video_id},
                    'timestamp': int(timezone.now().timestamp() * 1000),
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'K'
                }, ensure_ascii=False) + '\n')
            # #endregion
            return JsonResponse({'error': 'Видеофайл не найден'}, status=404)
        except Exception as e:
            # #region agent log
            import json as json_module
            log_path = os.path.join(settings.BASE_DIR, '.cursor', 'debug.log')
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({
                    'location': 'views_video_processing.py:66',
                    'message': 'ProcessVideoView error',
                    'data': {
                        'error': str(e),
                        'error_type': type(e).__name__,
                        'video_id': video_id
                    },
                    'timestamp': int(timezone.now().timestamp() * 1000),
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'L'
                }, ensure_ascii=False) + '\n')
            # #endregion
            logger.error(f'Ошибка обработки видео {video_id}: {str(e)}', exc_info=True)
            return JsonResponse({
                'error': f'Ошибка обработки: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ResetStuckVideosView(View):
    """API endpoint для сброса застрявших видео"""
    
    def post(self, request):
        """Сбросить застрявшие видео в статусе processing"""
        from datetime import timedelta
        import os
        
        try:
            hours = int(request.POST.get('hours', 2))
            cutoff_time = timezone.now() - timedelta(hours=hours)
            
            stuck_videos = VideoFile.objects.filter(
                status='processing',
                created_at__lt=cutoff_time
            )
            
            reset_count = 0
            errors = []
            
            for video in stuck_videos:
                file_exists = os.path.exists(video.file_path) if video.file_path else False
                
                try:
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
                    reset_count += 1
                except Exception as e:
                    errors.append({
                        'video_id': video.id,
                        'file_name': video.file_name,
                        'error': str(e)
                    })
                    logger.error(f'Ошибка сброса видео {video.id}: {e}', exc_info=True)
            
            return JsonResponse({
                'success': True,
                'message': f'Сброшено {reset_count} застрявших видео',
                'reset_count': reset_count,
                'errors': errors
            })
            
        except Exception as e:
            logger.error(f'Ошибка сброса застрявших видео: {str(e)}', exc_info=True)
            return JsonResponse({
                'error': f'Ошибка: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ProcessNextPendingVideoView(View):
    """API endpoint для обработки следующего ожидающего видео"""

    def post(self, request):
        try:
            logger.info('Запрос обработки следующего видео')
            from lessons.services.video_watcher import VideoWatcher
            watcher = VideoWatcher()
            watcher.process_existing_files()

            video_file = (
                VideoFile.objects
                .exclude(status='done')
                .order_by('created_at')
                .first()
            )

            if not video_file:
                logger.info('Нет видео для обработки')
                return JsonResponse({
                    'error': 'Новых видео для обработки нет'
                }, status=404)

            if video_file.status in ('error', 'processing'):
                logger.info(
                    'Видео %s в статусе %s, переустанавливаем в pending',
                    video_file.file_name,
                    video_file.status,
                )
                video_file.status = 'pending'
                video_file.error_message = None
                video_file.save()

            processor = VideoProcessor()
            logger.info(
                'Начинаем обработку видео: %s (id=%s)',
                video_file.file_name,
                video_file.id,
            )
            lesson = processor.process_video(video_file)

            response_data = {
                'success': True,
                'message': 'Видео успешно обработано',
                'lesson_id': lesson.id,
                'lesson_title': lesson.title,
                'cards_count': lesson.cards.count(),
                'video_id': video_file.id,
                'video_file_name': video_file.file_name,
            }
            logger.info(
                'Обработка завершена успешно: урок id=%s, карточек=%s',
                lesson.id,
                response_data['cards_count'],
            )
            return JsonResponse(response_data)

        except Exception as e:
            logger.error(f'Ошибка обработки следующего видео: {str(e)}', exc_info=True)
            return JsonResponse({
                'error': f'Ошибка обработки: {str(e)}'
            }, status=500)

