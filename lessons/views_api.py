"""
API endpoints для работы с уроками
Размер: ~150 строк
"""
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from lessons.models import Lesson, UserProgress, LessonAttempt, CardAttempt

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(['GET'])
def list_lessons(request):
    """Получить список всех уроков с прогрессом пользователя"""
    import json
    import traceback
    from django.db import connection
    
    logger.info('=== API list_lessons called ===')
    
    # Log database info
    db_info = connection.settings_dict
    logger.info(f'Database: {db_info.get("ENGINE", "unknown")}, Name: {db_info.get("NAME", "unknown")}')
    
    try:
        # Оптимизация: используем prefetch_related для карточек и select_related для видео
        # Это предотвращает N+1 запросы
        lessons = Lesson.objects.select_related('video').prefetch_related('cards').order_by('created_at')
        lessons_count = lessons.count()
        logger.info(f'Found {lessons_count} lessons in database')
        
        if lessons_count == 0:
            logger.warning('No lessons found in database!')
            logger.warning(f'Database engine: {db_info.get("ENGINE")}, Database name: {db_info.get("NAME")}')
            # Try to check if we're using wrong database
            try:
                from lessons.models import VideoFile
                video_count = VideoFile.objects.count()
                logger.info(f'Videos in database: {video_count}')
            except Exception as ve:
                logger.error(f'Error checking videos: {ve}')
            
            return JsonResponse({'lessons': [], 'message': 'No lessons found', 'database': db_info.get('ENGINE', 'unknown')})
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f'Error fetching lessons: {e}\n{error_trace}', exc_info=True)
        return JsonResponse({'error': str(e), 'lessons': [], 'traceback': error_trace}, status=500)
    
    # Получаем прогресс пользователя
    session_key = request.session.session_key
    user_progress = None
    if session_key:
        try:
            user_progress = UserProgress.objects.get(session_key=session_key)
        except UserProgress.DoesNotExist:
            pass
    
    # Оптимизация: предзагружаем все попытки уроков и карточки одним запросом
    lesson_attempts_map = {}
    card_attempts_map = {}
    if user_progress:
        lesson_attempts = LessonAttempt.objects.filter(
            user_progress=user_progress
        ).select_related('lesson').prefetch_related('card_attempts__card')
        
        for attempt in lesson_attempts:
            lesson_attempts_map[attempt.lesson_id] = attempt
            card_attempts = attempt.card_attempts.exclude(card_status=0)
            card_attempts_map[attempt.lesson_id] = {ca.card_id: ca for ca in card_attempts}
    
    lessons_data = []
    for lesson in lessons:
        # Оптимизация: используем prefetched карточки вместо запроса к БД
        cards = list(lesson.cards.all())
        topics = set(card.topic or 'general' for card in cards)
        topics_count = len(topics)
        cards_total = len(cards)
        
        # Подсчитываем прогресс по уроку
        progress_data = {
            'topics_completed': 0,
            'topics_total': topics_count,
            'cards_completed': 0,
            'cards_total': cards_total,
            'completion_percent': 0
        }
        
        if user_progress:
            # Оптимизация: используем предзагруженные данные вместо запросов к БД
            lesson_attempt = lesson_attempts_map.get(lesson.id)
            
            if lesson_attempt:
                # Оптимизация: используем предзагруженные card_attempts
                card_attempts = card_attempts_map.get(lesson.id, {})
                progress_data['cards_completed'] = len(card_attempts)
                
                # Подсчитываем пройденные темы (темы, где хотя бы одна карточка пройдена)
                completed_topics = set()
                for card_id, ca in card_attempts.items():
                    # Находим карточку в предзагруженных карточках
                    card = next((c for c in cards if c.id == card_id), None)
                    if card:
                        topic = card.topic or 'general'
                        completed_topics.add(topic)
                
                progress_data['topics_completed'] = len(completed_topics)
                
                # Процент выполнения
                if progress_data['cards_total'] > 0:
                    progress_data['completion_percent'] = int(
                        (progress_data['cards_completed'] / progress_data['cards_total']) * 100
                    )
        
        # Определяем, завершён ли урок (все карточки пройдены)
        user_completed = False
        if user_progress and progress_data['cards_total'] > 0:
            user_completed = progress_data['cards_completed'] == progress_data['cards_total']
            logger.debug(
                f'Lesson {lesson.id}: cards_completed={progress_data["cards_completed"]}, '
                f'cards_total={progress_data["cards_total"]}, user_completed={user_completed}'
            )
        
        lessons_data.append({
            'id': lesson.id,
            'title': lesson.title,
            'description': lesson.description,
            'language_level': lesson.language_level,
            'created_at': lesson.created_at.isoformat(),
            'cards_count': cards_total,  # Используем предвычисленное значение
            'video_file': lesson.video.file_name if lesson.video else None,
            'video_id': lesson.video.id if lesson.video else None,
            'topics_count': topics_count,
            'progress': progress_data,
            'user_completed': user_completed  # Добавляем поле для карты
        })
    
    logger.info(f'Returning {len(lessons_data)} lessons, user_progress={user_progress is not None}')
    
    try:
        response_data = {'lessons': lessons_data}
        if lessons_data:
            logger.info(f'First lesson: id={lessons_data[0].get("id")}, title={lessons_data[0].get("title", "N/A")}')
        return JsonResponse(response_data)
    except Exception as e:
        logger.error(f'Error creating JSON response: {e}', exc_info=True)
        return JsonResponse({'error': str(e), 'lessons': []}, status=500)


@csrf_exempt
@require_http_methods(['GET'])
def get_lesson(request, lesson_id):
    """Получить детальную информацию об уроке с карточками"""
    try:
        lesson = Lesson.objects.get(id=lesson_id)
        
        cards_data = []
        for card in lesson.cards.all().order_by('order_index'):
            cards_data.append({
                'id': card.id,
                'card_type': card.card_type,
                'question_text': card.question_text,
                'prompt_text': card.prompt_text,
                'correct_answer': card.correct_answer,
                'options': card.options,
                'extra_data': card.extra_data,
                'image_url': card.image_url,
                'icon_name': card.icon_name,
                'translation_text': card.translation_text,
                'hint_text': card.hint_text,
                'order_index': card.order_index
            })
        
        lesson_data = {
            'id': lesson.id,
            'title': lesson.title,
            'description': lesson.description,
            'language_level': lesson.language_level,
            'transcript_text': lesson.transcript_text,
            'raw_ai_response': lesson.raw_ai_response,
            'created_at': lesson.created_at.isoformat(),
            'cards': cards_data
        }
        
        return JsonResponse(lesson_data)
        
    except Lesson.DoesNotExist:
        return JsonResponse({'error': 'Урок не найден'}, status=404)


@csrf_exempt
@require_http_methods(['GET'])
def get_lesson_topics(request, lesson_id):
    """Получить темы урока с количеством карточек"""
    try:
        lesson = Lesson.objects.get(id=lesson_id)
        
        # Группируем карточки по темам
        topics_data = {}
        for card in lesson.cards.all().order_by('order_index'):
            topic = card.topic or 'general'
            if topic not in topics_data:
                topics_data[topic] = {
                    'topic': topic,
                    'cards_count': 0,
                    'cards': []
                }
            topics_data[topic]['cards_count'] += 1
            topics_data[topic]['cards'].append({
                'id': card.id,
                'card_type': card.card_type,
                'question_text': card.question_text,
                'order_index': card.order_index
            })
        
        # Преобразуем в список
        topics_list = []
        topic_names = {
            'weather': 'Погода',
            'actions': 'Действия',
            'colors': 'Цвета',
            'animals': 'Животные',
            'food': 'Еда',
            'family': 'Семья',
            'body': 'Части тела',
            'numbers': 'Числа',
            'general': 'Общее'
        }
        
        for topic, data in topics_data.items():
            topics_list.append({
                'topic': topic,
                'topic_name': topic_names.get(topic, topic),
                'cards_count': data['cards_count']
            })
        
        return JsonResponse({
            'lesson_id': lesson.id,
            'lesson_title': lesson.title,
            'topics': topics_list
        })
        
    except Lesson.DoesNotExist:
        return JsonResponse({'error': 'Урок не найден'}, status=404)

