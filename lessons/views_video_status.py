"""
Views для получения статуса обработки видео
Размер: ~60 строк
"""
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from lessons.models import VideoFile

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(['GET'])
def get_processing_status(request):
    """Получить статус обработки видео и логи"""
    try:
        from lessons.services.log_storage import LogStorage
        
        # Оптимизация: используем агрегацию для подсчета
        total_videos = VideoFile.objects.count()
        pending_videos = VideoFile.objects.filter(status='pending').count()
        processing_videos = VideoFile.objects.filter(status='processing').count()
        done_videos = VideoFile.objects.filter(status='done').count()
        error_videos = VideoFile.objects.filter(status='error').count()
        
        # Оптимизация: используем select_related
        current_video = VideoFile.objects.filter(status='processing').select_related('lesson').order_by('created_at').first()
        current_video_info = None
        if current_video:
            all_videos_ordered = VideoFile.objects.all().order_by('created_at')
            video_ids = list(all_videos_ordered.values_list('id', flat=True))
            try:
                current_index = video_ids.index(current_video.id) + 1
            except ValueError:
                current_index = 0
            current_video_info = {
                'id': current_video.id,
                'file_name': current_video.file_name,
                'index': current_index,
                'total': total_videos,
                'processing_message': current_video.processing_message,
                'processing_status': current_video.processing_status
            }
        
        is_processing = processing_videos > 0 or pending_videos > 0
        
        log_storage = LogStorage.get_instance()
        logs = log_storage.get_logs(limit=200)
        
        return JsonResponse({
            'is_processing': is_processing,
            'total_videos': total_videos,
            'pending': pending_videos,
            'processing': processing_videos,
            'done': done_videos,
            'error': error_videos,
            'current_video': current_video_info,
            'progress_percent': int((done_videos / total_videos * 100)) if total_videos > 0 else 0,
            'logs': logs
        })
        
    except Exception as e:
        logger.error(f'Ошибка получения статуса обработки: {str(e)}', exc_info=True)
        return JsonResponse({
            'error': f'Ошибка: {str(e)}'
        }, status=500)

