"""
Views для панели учителя
"""
import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from lessons.models import VideoFile, Lesson

logger = logging.getLogger(__name__)


def teacher_panel(request):
    """Панель учителя для загрузки и управления видео"""
    videos = VideoFile.objects.all().order_by('-created_at')
    lessons = Lesson.objects.all().order_by('-created_at')
    
    context = {
        'videos': videos,
        'lessons': lessons,
        'total_videos': videos.count(),
        'pending_videos': videos.filter(status='pending').count(),
        'processing_videos': videos.filter(status='processing').count(),
        'done_videos': videos.filter(status='done').count(),
        'error_videos': videos.filter(status='error').count(),
    }
    return render(request, 'lessons/teacher_panel.html', context)

