"""
Базовые views для работы с видео
Размер: ~100 строк
"""
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from lessons.models import VideoFile

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(['GET'])
def list_videos(request):
    """Получить список всех видеофайлов"""
    videos = VideoFile.objects.all().order_by('-created_at')
    
    videos_data = []
    for video in videos:
        videos_data.append({
            'id': video.id,
            'file_name': video.file_name,
            'file_path': video.file_path,
            'status': video.status,
            'created_at': video.created_at.isoformat(),
            'processed_at': video.processed_at.isoformat() if video.processed_at else None,
            'error_message': video.error_message,
            'has_lesson': hasattr(video, 'lesson')
        })
    
    return JsonResponse({'videos': videos_data})


@csrf_exempt
@require_http_methods(['GET'])
def get_video_status(request, video_id):
    """Получить статус обработки конкретного видео"""
    from django.utils import timezone
    from datetime import timedelta
    import os
    
    try:
        video_file = VideoFile.objects.get(id=video_id)
        
        # Расчет прогресса и времени
        progress_percent = 0
        estimated_seconds_remaining = 0
        elapsed_seconds = 0
        
        if video_file.status == 'processing':
            # Время с начала обработки
            elapsed_seconds = int((timezone.now() - video_file.created_at).total_seconds())
            
            # Оценка времени на основе размера файла
            file_size_mb = (video_file.file_size / (1024 * 1024)) if video_file.file_size else 50
            total_estimated_seconds = max(30, min(900, int(file_size_mb * 2.5)))
            
            # Прогресс на основе статуса обработки
            if video_file.processing_status == 'transcribing':
                progress_percent = min(30, int((elapsed_seconds / total_estimated_seconds) * 30))
            elif video_file.processing_status == 'generating_lesson':
                progress_percent = min(90, 30 + int((elapsed_seconds / total_estimated_seconds) * 60))
            else:
                progress_percent = 0
            
            # Оставшееся время
            if progress_percent > 0:
                estimated_seconds_remaining = max(0, int((total_estimated_seconds * (100 - progress_percent)) / 100))
            else:
                estimated_seconds_remaining = total_estimated_seconds
        
        return JsonResponse({
            'id': video_file.id,
            'file_name': video_file.file_name,
            'status': video_file.status,
            'processing_status': video_file.processing_status,
            'processing_message': video_file.processing_message,
            'error_message': video_file.error_message,
            'has_lesson': hasattr(video_file, 'lesson'),
            'lesson_id': video_file.lesson.id if hasattr(video_file, 'lesson') else None,
            'lesson_title': video_file.lesson.title if hasattr(video_file, 'lesson') else None,
            'progress_percent': progress_percent,
            'estimated_seconds_remaining': estimated_seconds_remaining,
            'elapsed_seconds': elapsed_seconds,
            'file_size_mb': round((video_file.file_size / (1024 * 1024)) if video_file.file_size else 0, 2),
        })
    except VideoFile.DoesNotExist:
        return JsonResponse({'error': 'Видеофайл не найден'}, status=404)
    except Exception as e:
        logger.error(f'Ошибка получения статуса видео {video_id}: {str(e)}', exc_info=True)
        return JsonResponse({'error': f'Ошибка: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(['GET'])
def get_next_pending_video_info(request):
    """Получить информацию о следующем видео для обработки"""
    try:
        logger.info('Запрос информации о следующем видео для обработки')
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
            logger.info('Нет видео, которые можно обработать')
            return JsonResponse({
                'error': 'Новых видео для обработки нет'
            }, status=404)

        file_size_mb = (video_file.file_size / (1024 * 1024)) if video_file.file_size else 50
        estimated_seconds = max(30, min(900, int(file_size_mb * 2.5)))

        response_data = {
            'video_id': video_file.id,
            'file_name': video_file.file_name,
            'file_size_mb': round(file_size_mb, 2),
            'estimated_seconds': estimated_seconds,
            'status': video_file.status,
        }
        logger.info(
            'Найдено видео для обработки: %s (%.2f MB, ~%s сек)',
            video_file.file_name,
            response_data['file_size_mb'],
            estimated_seconds,
        )
        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f'Ошибка получения информации о видео: {str(e)}', exc_info=True)
        return JsonResponse({
            'error': f'Ошибка: {str(e)}'
        }, status=500)

