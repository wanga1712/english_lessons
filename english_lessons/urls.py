"""
URL configuration for english_lessons project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from lessons.views import home
from lessons.views_api import list_lessons, get_lesson, get_lesson_topics
from lessons.views_video import (
    list_videos, ProcessVideoView, ProcessNextPendingVideoView,
    get_next_pending_video_info, ProcessAllVideosView, RecreateAllLessonsView,
    get_processing_status
)
from lessons.views_progress import (
    get_user_progress, start_lesson_attempt,
    submit_card_answer, complete_lesson_attempt
)
from lessons.views_lesson import view_lesson, view_lesson_topics, view_card_exercise, get_card_statuses
from lessons.views_uchi import lesson_topics_uchi, home_uchi
from lessons.views_teacher import teacher_panel

urlpatterns = [
    path('', home, name='home'),
    path('teacher/', teacher_panel, name='teacher_panel'),
    path('admin/', admin.site.urls),
    # Стандартные страницы
    path('lesson/<int:lesson_id>/', view_lesson_topics, name='view_lesson_topics'),
    path('lesson/<int:lesson_id>/topic/<str:topic>/', view_lesson, name='view_lesson'),
    path('lesson/<int:lesson_id>/card/<int:card_id>/', view_card_exercise, name='view_card_exercise'),
    # Стиль Uchi.ru
    path('uchi/', home_uchi, name='home_uchi'),
    path('lesson/<int:lesson_id>/uchi/', lesson_topics_uchi, name='lesson_topics_uchi'),
    path('api/lessons/', list_lessons, name='list_lessons'),
    path('api/lessons/<int:lesson_id>/', get_lesson, name='get_lesson'),
    path('api/lessons/<int:lesson_id>/topics/', get_lesson_topics, name='get_lesson_topics'),
    path('api/videos/', list_videos, name='list_videos'),
    path(
        'api/videos/<int:video_id>/process/',
        ProcessVideoView.as_view(),
        name='process_video',
    ),
    path(
        'api/videos/process_next/',
        ProcessNextPendingVideoView.as_view(),
        name='process_next_video',
    ),
    path(
        'api/videos/process_all/',
        ProcessAllVideosView.as_view(),
        name='process_all_videos',
    ),
    path(
        'api/videos/recreate_all_lessons/',
        RecreateAllLessonsView.as_view(),
        name='recreate_all_lessons',
    ),
    path(
        'api/videos/processing_status/',
        get_processing_status,
        name='processing_status',
    ),
    path(
        'api/videos/next_pending_info/',
        get_next_pending_video_info,
        name='next_pending_video_info',
    ),
    # API для работы с прогрессом
    path('api/progress/', get_user_progress, name='get_user_progress'),
    path('api/lessons/<int:lesson_id>/start/', start_lesson_attempt, name='start_lesson_attempt'),
    path('api/cards/answer/', submit_card_answer, name='submit_card_answer'),
    path('api/attempts/<int:attempt_id>/complete/', complete_lesson_attempt, name='complete_lesson_attempt'),
    path('api/lessons/<int:lesson_id>/card_statuses/', get_card_statuses, name='get_card_statuses'),
]

# Добавляем обработку статических файлов для разработки
# ВАЖНО: В продакшене используйте веб-сервер (nginx/apache) для статики!
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Всегда обслуживаем статику через staticfiles (работает из STATICFILES_DIRS)
urlpatterns += staticfiles_urlpatterns()

# Также обслуживаем из STATIC_ROOT напрямую
if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Обслуживаем статику из STATICFILES_DIRS напрямую (приоритет)
for static_dir in settings.STATICFILES_DIRS:
    urlpatterns += static(settings.STATIC_URL, document_root=str(static_dir))
