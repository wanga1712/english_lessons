"""
Основные views для приложения
Размер: ~50 строк
"""
from django.shortcuts import render
from django.http import HttpResponse

# Импортируем views из других модулей
from lessons.views_api import list_lessons, get_lesson
from lessons.views_video import (
    list_videos, ProcessVideoView, ProcessNextPendingVideoView,
    get_next_pending_video_info
)
from lessons.views_progress import (
    get_user_progress, start_lesson_attempt,
    submit_card_answer, complete_lesson_attempt
)


def home(request):
    """Главная страница - редирект на новую карту приключений"""
    from django.shortcuts import redirect
    # Редирект на новую карту с игровым интерфейсом
    return redirect('home_uchi')


# home_uchi теперь находится в lessons.views_uchi
