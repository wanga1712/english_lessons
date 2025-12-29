"""
Views для панели учителя
"""
import json
import os
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from lessons.models import VideoFile, Lesson

logger = logging.getLogger(__name__)


def teacher_panel(request):
    """Панель учителя для загрузки и управления видео"""
    # #region agent log
    watched_dir = settings.WATCHED_VIDEO_DIRECTORY
    watched_dir_exists = os.path.exists(watched_dir)
    with open('.cursor/debug.log', 'a', encoding='utf-8') as f:
        f.write(json.dumps({
            'location': 'views_teacher.py:20',
            'message': 'teacher_panel called',
            'data': {
                'WATCHED_VIDEO_DIRECTORY': watched_dir,
                'directory_exists': watched_dir_exists,
                'directory_abs': os.path.abspath(watched_dir) if watched_dir else None
            },
            'timestamp': int(timezone.now().timestamp() * 1000),
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'A'
        }, ensure_ascii=False) + '\n')
    # #endregion
    
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
        'watched_video_directory': settings.WATCHED_VIDEO_DIRECTORY,
    }
    return render(request, 'lessons/teacher_panel.html', context)


@csrf_exempt
@require_http_methods(['POST'])
def upload_video(request):
    """Endpoint для загрузки видеофайлов"""
    # #region agent log
    watched_dir = settings.WATCHED_VIDEO_DIRECTORY
    with open('.cursor/debug.log', 'a', encoding='utf-8') as f:
        f.write(json.dumps({
            'location': 'views_teacher.py:45',
            'message': 'upload_video called',
            'data': {
                'WATCHED_VIDEO_DIRECTORY': watched_dir,
                'directory_exists': os.path.exists(watched_dir),
                'files_count': len(request.FILES) if hasattr(request, 'FILES') else 0
            },
            'timestamp': int(timezone.now().timestamp() * 1000),
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'B'
        }, ensure_ascii=False) + '\n')
    # #endregion
    
    try:
        if 'videos' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'Нет файлов для загрузки'}, status=400)
        
        uploaded_files = []
        watched_dir = settings.WATCHED_VIDEO_DIRECTORY
        
        # Создаем директорию, если её нет
        os.makedirs(watched_dir, exist_ok=True)
        
        for video_file in request.FILES.getlist('videos'):
            # #region agent log
            with open('.cursor/debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'location': 'views_teacher.py:65',
                    'message': 'Processing uploaded file',
                    'data': {
                        'filename': video_file.name,
                        'size': video_file.size,
                        'target_directory': watched_dir
                    },
                    'timestamp': int(timezone.now().timestamp() * 1000),
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'C'
                }, ensure_ascii=False) + '\n')
            # #endregion
            
            # Сохраняем файл в WATCHED_VIDEO_DIRECTORY
            file_path = os.path.join(watched_dir, video_file.name)
            
            # Если файл уже существует, добавляем номер
            counter = 1
            original_path = file_path
            while os.path.exists(file_path):
                name, ext = os.path.splitext(video_file.name)
                file_path = os.path.join(watched_dir, f'{name}_{counter}{ext}')
                counter += 1
            
            # Сохраняем файл
            with open(file_path, 'wb+') as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)
            
            # #region agent log
            file_size = os.path.getsize(file_path)
            with open('.cursor/debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'location': 'views_teacher.py:90',
                    'message': 'File saved',
                    'data': {
                        'file_path': file_path,
                        'file_size': file_size,
                        'file_exists': os.path.exists(file_path)
                    },
                    'timestamp': int(timezone.now().timestamp() * 1000),
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D'
                }, ensure_ascii=False) + '\n')
            # #endregion
            
            # Нормализуем путь для БД
            file_path_normalized = os.path.normpath(file_path)
            
            # Проверяем, не существует ли уже запись
            existing_video = VideoFile.objects.filter(file_path=file_path_normalized).first()
            if existing_video:
                uploaded_files.append({
                    'id': existing_video.id,
                    'name': existing_video.file_name,
                    'status': 'exists'
                })
                continue
            
            # Создаем запись в БД
            video_record = VideoFile.objects.create(
                file_path=file_path_normalized,
                file_name=os.path.basename(file_path),
                file_size=file_size,
                status='pending'
            )
            
            # #region agent log
            with open('.cursor/debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'location': 'views_teacher.py:115',
                    'message': 'VideoFile created',
                    'data': {
                        'video_id': video_record.id,
                        'file_path': video_record.file_path,
                        'file_name': video_record.file_name
                    },
                    'timestamp': int(timezone.now().timestamp() * 1000),
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'E'
                }, ensure_ascii=False) + '\n')
            # #endregion
            
            uploaded_files.append({
                'id': video_record.id,
                'name': video_record.file_name,
                'status': 'uploaded'
            })
        
        return JsonResponse({
            'success': True,
            'message': f'Загружено файлов: {len(uploaded_files)}',
            'files': uploaded_files
        })
        
    except Exception as e:
        # #region agent log
        with open('.cursor/debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'location': 'views_teacher.py:135',
                'message': 'upload_video error',
                'data': {
                    'error': str(e),
                    'error_type': type(e).__name__
                },
                'timestamp': int(timezone.now().timestamp() * 1000),
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'F'
            }, ensure_ascii=False) + '\n')
        # #endregion
        logger.error(f'Ошибка загрузки видео: {str(e)}', exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

