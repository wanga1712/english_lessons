"""
Views для UI в стиле Uchi.ru
Размер: ~150 строк
"""
import json
import logging
from django.shortcuts import render, get_object_or_404
from lessons.models import Lesson, UserProgress, UserAvatar, LessonAttempt, CardAttempt
from lessons.views_progress import _get_or_create_user_progress

logger = logging.getLogger(__name__)


def home_uchi(request):
    """Главная страница в стиле Uchi.ru - карта приключений"""
    user_progress = None
    avatar_data = None

    try:
        user_progress = _get_or_create_user_progress(request)
        try:
            avatar = UserAvatar.objects.get(user_progress=user_progress)
            avatar_data = {
                'name': avatar.avatar_name,
                'emoji': avatar.avatar_emoji,
                'score': avatar.total_score
            }
        except UserAvatar.DoesNotExist:
            avatar_data = {'name': 'Ученик', 'emoji': '🎓', 'score': 0.0}
    except Exception as e:
        logger.error(f"Error getting user progress or avatar for Uchi home: {e}", exc_info=True)
        avatar_data = {'name': 'Ученик', 'emoji': '🎓', 'score': 0.0}

    context = {
        'user_progress': user_progress,
        'avatar_data': avatar_data,
        'avatar_data_json': json.dumps(avatar_data)
    }
    # Use hero map template with Canvas and character sprite
    return render(request, 'lessons/home_uchi_hero.html', context)


def lesson_topics_uchi(request, lesson_id):
    """Страница тем урока в стиле Uchi.ru"""
    logger.info(f'=== lesson_topics_uchi called for lesson_id={lesson_id} ===')
    
    lesson = get_object_or_404(Lesson.objects.prefetch_related('cards'), id=lesson_id)
    logger.info(f'Lesson found: id={lesson.id}, title={lesson.title}')
    
    # Получаем прогресс пользователя
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    user_progress = None
    avatar_data = None
    card_statuses = {}
    
    try:
        user_progress = UserProgress.objects.get(session_key=session_key)
        logger.info(f'User progress found: session_key={session_key}')
        lesson_attempt = LessonAttempt.objects.filter(
            user_progress=user_progress,
            lesson=lesson
        ).select_related('user_progress').prefetch_related('card_attempts__card').order_by('-started_at').first()
        
        if lesson_attempt:
            logger.info(f'Lesson attempt found: id={lesson_attempt.id}')
            for ca in lesson_attempt.card_attempts.all():
                card_statuses[ca.card.id] = ca.card_status
            logger.info(f'Card statuses loaded: {len(card_statuses)} cards')
        
        try:
            avatar = UserAvatar.objects.get(user_progress=user_progress)
            avatar_data = {
                'name': avatar.avatar_name,
                'emoji': avatar.avatar_emoji,
                'score': avatar.total_score
            }
        except UserAvatar.DoesNotExist:
            avatar_data = {'name': 'Ученик', 'emoji': '🦊', 'score': 0.0}
    except UserProgress.DoesNotExist:
        logger.info('User progress not found, using defaults')
        avatar_data = {'name': 'Ученик', 'emoji': '🦊', 'score': 0.0}
    
    # Группируем карточки по темам
    cards = list(lesson.cards.all().order_by('order_index'))
    logger.info(f'Total cards in lesson: {len(cards)}')
    
    topics_data = {}
    topic_names = {
        'weather': 'Погода',
        'actions': 'Действия',
        'colors': 'Цвета',
        'animals': 'Животные',
        'food': 'Еда',
        'family': 'Семья',
        'body': 'Части тела',
        'numbers': 'Числа',
        'general': 'Общее',
        'review': 'Повторение'
    }
    
    for card in cards:
        topic = card.topic or 'general'
        logger.debug(f'Card {card.id}: topic={topic}')
        if topic not in topics_data:
            topics_data[topic] = {
                'topic': topic,
                'topic_name': topic_names.get(topic, topic),
                'cards_count': 0,
                'cards_completed': 0,
                'completion_percent': 0
            }
        topics_data[topic]['cards_count'] += 1
        
        # Проверяем, пройдена ли карточка
        if card.id in card_statuses and card_statuses[card.id] > 0:
            topics_data[topic]['cards_completed'] += 1
    
    logger.info(f'Topics found: {len(topics_data)} topics')
    for topic, data in topics_data.items():
        logger.info(f'  Topic {topic}: {data["cards_count"]} cards, {data["cards_completed"]} completed')
    
    # Вычисляем процент выполнения для каждой темы
    for topic_data in topics_data.values():
        if topic_data['cards_count'] > 0:
            topic_data['completion_percent'] = int(
                (topic_data['cards_completed'] / topic_data['cards_count']) * 100
            )
    
    topics_list = sorted(topics_data.values(), key=lambda x: x['topic'])
    logger.info(f'Returning {len(topics_list)} topics to template')
    
    context = {
        'lesson': lesson,
        'topics': topics_list,
        'user_progress': user_progress,
        'avatar_data': avatar_data
    }
    
    return render(request, 'lessons/lesson_topics_uchi.html', context)

