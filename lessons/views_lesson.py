"""
View для отображения интерактивного урока с карточками
"""
import json
import logging
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from lessons.models import Lesson, LessonAttempt, CardAttempt, UserProgress, UserAvatar, ExerciseCard

logger = logging.getLogger(__name__)


def view_lesson_topics(request, lesson_id):
    """Страница просмотра тем урока"""
    # Оптимизация: используем prefetch_related для карточек
    lesson = get_object_or_404(Lesson.objects.prefetch_related('cards'), id=lesson_id)
    
    # Получаем прогресс пользователя
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    user_progress = None
    lesson_attempt = None
    card_statuses = {}
    
    try:
        user_progress = UserProgress.objects.get(session_key=session_key)
        # Оптимизация: используем select_related и prefetch_related
        lesson_attempt = LessonAttempt.objects.filter(
            user_progress=user_progress,
            lesson=lesson
        ).select_related('user_progress').prefetch_related('card_attempts__card').order_by('-started_at').first()
        
        if lesson_attempt:
            # Оптимизация: используем предзагруженные card_attempts
            for ca in lesson_attempt.card_attempts.all():
                card_statuses[ca.card.id] = ca.card_status
    except UserProgress.DoesNotExist:
        pass
    
    # Группируем карточки по темам
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
    
    for card in lesson.cards.all().order_by('order_index'):
        topic = card.topic or 'general'
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
    
    # Вычисляем процент выполнения для каждой темы
    for topic_data in topics_data.values():
        if topic_data['cards_count'] > 0:
            topic_data['completion_percent'] = int(
                (topic_data['cards_completed'] / topic_data['cards_count']) * 100
            )
    
    topics_list = sorted(topics_data.values(), key=lambda x: x['topic'])
    
    # Получаем данные аватара
    avatar_data = None
    if user_progress:
        try:
            avatar = UserAvatar.objects.get(user_progress=user_progress)
            avatar_data = {
                'name': avatar.avatar_name,
                'emoji': avatar.avatar_emoji,
                'score': avatar.total_score
            }
        except UserAvatar.DoesNotExist:
            avatar_data = {'name': 'Ученик', 'emoji': '🎓', 'score': 0.0}
    else:
        avatar_data = {'name': 'Ученик', 'emoji': '🎓', 'score': 0.0}
    
    context = {
        'lesson': lesson,
        'topics': topics_list,
        'topics_json': json.dumps(topics_list),
        'user_progress': user_progress,
        'avatar_data': avatar_data
    }
    
    return render(request, 'lessons/lesson_topics.html', context)


def view_lesson(request, lesson_id, topic=None):
    """Интерактивная HTML страница для прохождения урока с карточками"""
    # Оптимизация: используем prefetch_related для карточек
    lesson = get_object_or_404(Lesson.objects.prefetch_related('cards'), id=lesson_id)
    
    # Получаем или создаём прогресс пользователя
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    user_progress = None
    card_statuses = {}
    avatar_data = None
    
    try:
        user_progress = UserProgress.objects.get(session_key=session_key)
        # Оптимизация: используем select_related и prefetch_related
        lesson_attempt = LessonAttempt.objects.filter(
            user_progress=user_progress,
            lesson=lesson
        ).select_related('user_progress').prefetch_related('card_attempts__card').order_by('-started_at').first()
        
        if lesson_attempt:
            # Оптимизация: используем предзагруженные card_attempts
            for ca in lesson_attempt.card_attempts.all():
                card_statuses[ca.card.id] = {
                    'status': ca.card_status,
                    'color': ca.get_status_color(),
                    'attempts_count': ca.attempts_count
                }
        
        # Оптимизация: используем select_related для аватара
        try:
            avatar = UserAvatar.objects.select_related('user_progress').get(user_progress=user_progress)
            avatar_data = {
                'name': avatar.avatar_name,
                'emoji': avatar.avatar_emoji,
                'score': avatar.total_score
            }
        except UserAvatar.DoesNotExist:
            avatar_data = {'name': 'Ученик', 'emoji': '🎓', 'score': 0.0}
    except UserProgress.DoesNotExist:
        pass
    
    # Фильтруем карточки по теме, если указана
    if topic:
        cards = lesson.cards.filter(topic=topic).order_by('order_index')
    else:
        cards = lesson.cards.all().order_by('order_index')
    
    # Подготавливаем данные карточек для JavaScript
    cards_data = []
    topics_set = set()
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
        card_topic = card.topic or 'general'
        topics_set.add(card_topic)
        card_status = card_statuses.get(card.id, {'status': 0, 'color': 'gray', 'attempts_count': 0})
        
        # Очищаем экранированные кавычки из текста
        def clean_text(text):
            if not text:
                return ''
            return str(text).replace("\\'", "'").replace('\\"', '"').strip()
        
        cards_data.append({
            'id': card.id,
            'card_type': card.card_type,
            'question_text': clean_text(card.question_text),
            'prompt_text': clean_text(card.prompt_text),
            'correct_answer': clean_text(card.correct_answer) if card.correct_answer else None,
            'options': card.options,
            'extra_data': card.extra_data,
            'image_url': card.image_url,
            'icon_name': card.icon_name,
            'translation_text': clean_text(card.translation_text) if card.translation_text else None,
            'hint_text': clean_text(card.hint_text) if card.hint_text else None,
            'topic': card_topic,
            'topic_name': topic_names.get(card_topic, card_topic),
            'order_index': card.order_index,
            'card_status': card_status['status'],
            'status_color': card_status['color'],
            'attempts_count': card_status['attempts_count'],
        })
    
    # Группируем карточки по темам для удобства
    topics_data = {}
    for card_data in cards_data:
        topic = card_data['topic']
        if topic not in topics_data:
            topics_data[topic] = {
                'name': card_data['topic_name'],
                'cards': []
            }
        topics_data[topic]['cards'].append(card_data)
    
    # Если указана тема, показываем только карточки этой темы
    if topic:
        filtered_topics_data = {topic: topics_data.get(topic, {'name': topic_names.get(topic, topic), 'cards': []})}
        topics_data = filtered_topics_data
    
    context = {
        'lesson': lesson,
        'cards_data_json': json.dumps(cards_data),
        'topics_data_json': json.dumps(topics_data),
        'topics_list': sorted(list(topics_set)),
        'current_topic': topic_names.get(topic, topic) if topic else None,
        'avatar_data_json': json.dumps(avatar_data) if avatar_data else 'null',
        'user_progress_json': json.dumps({
            'total_experience': user_progress.total_experience if user_progress else 0,
            'current_level': user_progress.current_level if user_progress else 1
        }),
    }
    
    return render(request, 'lessons/lesson_grid.html', context)


@csrf_exempt
@require_http_methods(['GET'])
def get_card_statuses(request, lesson_id):
    """Получить статусы всех карточек урока"""
    try:
        # Оптимизация: используем prefetch_related
        lesson = Lesson.objects.prefetch_related('cards').get(id=lesson_id)
        session_key = request.session.session_key
        
        if not session_key:
            return JsonResponse({'card_statuses': {}})
        
        user_progress = UserProgress.objects.filter(session_key=session_key).first()
        if not user_progress:
            return JsonResponse({'card_statuses': {}})
        
        # Оптимизация: используем select_related и prefetch_related
        lesson_attempt = LessonAttempt.objects.filter(
            user_progress=user_progress,
            lesson=lesson
        ).select_related('user_progress').prefetch_related('card_attempts__card').order_by('-started_at').first()
        
        card_statuses = {}
        if lesson_attempt:
            # Оптимизация: используем предзагруженные card_attempts
            for ca in lesson_attempt.card_attempts.all():
                card_statuses[ca.card.id] = {
                    'status': ca.card_status,
                    'color': ca.get_status_color(),
                    'attempts_count': ca.attempts_count
                }
        
        return JsonResponse({'card_statuses': card_statuses})
    except Exception as e:
        logger.error(f'Ошибка получения статусов карточек: {str(e)}', exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


def view_card_exercise(request, lesson_id, card_id):
    """Страница выполнения одной карточки"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    card = get_object_or_404(ExerciseCard, id=card_id, lesson=lesson)
    
    # Получаем или создаём прогресс пользователя
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    user_progress = None
    attempt_id = None
    
    try:
        user_progress = UserProgress.objects.get(session_key=session_key)
        # Получаем последнюю попытку урока или создаём новую
        lesson_attempt = LessonAttempt.objects.filter(
            user_progress=user_progress,
            lesson=lesson
        ).order_by('-started_at').first()
        
        if not lesson_attempt:
            lesson_attempt = LessonAttempt.objects.create(
                user_progress=user_progress,
                lesson=lesson,
                status='in_progress',
                total_cards=lesson.cards.count()
            )
        
        attempt_id = lesson_attempt.id
    except UserProgress.DoesNotExist:
        pass
    
    # Получаем данные аватара
    avatar_data = None
    if user_progress:
        try:
            avatar = UserAvatar.objects.get(user_progress=user_progress)
            avatar_data = {
                'name': avatar.avatar_name,
                'emoji': avatar.avatar_emoji,
                'score': avatar.total_score
            }
        except UserAvatar.DoesNotExist:
            avatar_data = {'name': 'Ученик', 'emoji': '🎓', 'score': 0.0}
    else:
        avatar_data = {'name': 'Ученик', 'emoji': '🎓', 'score': 0.0}
    
    # Функция для очистки экранированных кавычек
    def clean_text(text):
        if not text:
            return ''
        cleaned = str(text)
        cleaned = cleaned.replace("\\\\'", "'")
        cleaned = cleaned.replace('\\\\"', '"')
        cleaned = cleaned.replace("\\'", "'")
        cleaned = cleaned.replace('\\"', '"')
        cleaned = cleaned.replace("&#39;", "'")
        cleaned = cleaned.replace("&apos;", "'")
        cleaned = cleaned.replace("&quot;", '"')
        return cleaned.strip()
    
    question_text = clean_text(card.question_text) if card.question_text else ''
    prompt_text = clean_text(card.prompt_text) if card.prompt_text else ''
    correct_answer = clean_text(card.correct_answer) if card.correct_answer else None
    
    # Если question_text пустой, используем prompt_text или correct_answer
    if not question_text:
        question_text = prompt_text or (correct_answer if correct_answer else '')
    
    # Подготавливаем данные карточки
    card_data = {
        'id': card.id,
        'card_type': card.card_type,
        'question_text': question_text,
        'prompt_text': prompt_text,
        'correct_answer': correct_answer,
        'options': card.options,
        'extra_data': card.extra_data or {},
        'image_url': card.image_url,
        'icon_name': card.icon_name,
        'translation_text': clean_text(card.translation_text) if card.translation_text else None,
        'hint_text': clean_text(card.hint_text) if card.hint_text else None,
    }
    
    # Логируем для отладки
    logger.debug(f'Card data for card {card.id}: type={card.card_type}, question_text length={len(card.question_text) if card.question_text else 0}, extra_data={card.extra_data}')
    
    context = {
        'lesson': lesson,
        'card': card,
        'card_data_json': json.dumps(card_data, ensure_ascii=False),
        'attempt_id': attempt_id,
        'user_progress': user_progress,
        'avatar_data': avatar_data
    }
    
    return render(request, 'lessons/card_exercise.html', context)
