"""
Views для обработки видео - основной файл для импорта
Размер: ~20 строк
"""
# Импортируем views из модулей для обратной совместимости
from lessons.views_video_base import list_videos, get_next_pending_video_info
from lessons.views_video_processing import ProcessVideoView, ProcessNextPendingVideoView
from lessons.views_video_batch import ProcessAllVideosView, RecreateAllLessonsView
from lessons.views_video_status import get_processing_status

# Экспортируем все views для использования в urls.py
__all__ = [
    'list_videos',
    'ProcessVideoView',
    'get_next_pending_video_info',
    'ProcessNextPendingVideoView',
    'ProcessAllVideosView',
    'RecreateAllLessonsView',
    'get_processing_status',
]
