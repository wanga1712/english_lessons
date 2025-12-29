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
    from django.db import connection, DatabaseError
    
    logger.info('=== API list_lessons called ===')
    
    # Log database info
    db_info = connection.settings_dict
    db_engine = db_info.get("ENGINE", "unknown")
    db_name_raw = db_info.get("NAME", "unknown")
    # Преобразуем Path в строку для JSON сериализации
    db_name = str(db_name_raw) if db_name_raw else "unknown"
    logger.info(f'Database: {db_engine}, Name: {db_name}')
    
    # Проверяем, подключены ли мы к правильной базе данных
    is_english_lessons_db = 'english_lessons' in db_name.lower()
    logger.info(f'Is english_lessons database: {is_english_lessons_db}')
    
    # Проверяем подключение к базе данных
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        logger.info('Database connection test: SUCCESS')
    except Exception as conn_test_error:
        logger.error(f'Database connection test FAILED: {conn_test_error}', exc_info=True)
        return JsonResponse({
            'lessons': [],
            'error': 'database_connection_error',
            'error_message': 'Ошибка подключения к базе данных english_lessons',
            'error_details': str(conn_test_error),
            'database': db_name,
            'message': 'Не удалось подключиться к базе данных. Проверьте настройки подключения.'
        }, status=500)
    
    try:
        # Сначала проверим без фильтров - используем iterator() для больших таблиц
        try:
            all_lessons_raw = Lesson.objects.all()
            all_lessons_count = all_lessons_raw.count()
            logger.info(f'Total lessons in database (no filters): {all_lessons_count}')
            
            if all_lessons_count > 0:
                # Покажем первые несколько уроков для диагностики
                sample_lessons = list(all_lessons_raw[:5])
                for lesson in sample_lessons:
                    logger.info(f'  Sample lesson: id={lesson.id}, title="{lesson.title}", video_id={lesson.video_id if lesson.video else None}')
        except DatabaseError as db_error:
            error_msg = f'Database error while counting lessons: {str(db_error)}'
            logger.error(error_msg, exc_info=True)
            return JsonResponse({
                'lessons': [],
                'error': 'database_connection_error',
                'error_message': 'Ошибка подключения к базе данных english_lessons',
                'error_details': str(db_error),
                'database': db_name,
                'message': 'Не удалось подключиться к базе данных. Проверьте настройки подключения.'
            }, status=500)
        except Exception as count_error:
            error_msg = f'Error counting lessons: {count_error}'
            logger.error(error_msg, exc_info=True)
            all_lessons_count = 0
        
        # Оптимизация: используем prefetch_related для карточек и select_related для видео
        # Это предотвращает N+1 запросы
        # Ограничиваем количество загружаемых данных для избежания таймаутов
        try:
            lessons = Lesson.objects.select_related('video').prefetch_related('cards').order_by('created_at')
            lessons_count = lessons.count()
            logger.info(f'Found {lessons_count} lessons after select_related/prefetch_related')
        except Exception as query_error:
            logger.warning(f'Error with prefetch query: {query_error}')
            # Fallback: попробуем без prefetch для карточек (загрузим их позже)
            try:
                lessons = Lesson.objects.select_related('video').order_by('created_at')
                lessons_count = lessons.count()
                logger.info(f'Found {lessons_count} lessons (fallback without prefetch)')
            except Exception as fallback_error:
                logger.error(f'Error even without prefetch: {fallback_error}')
                # Последний fallback: простой запрос
                lessons = Lesson.objects.all().order_by('created_at')
                lessons_count = lessons.count()
                logger.info(f'Found {lessons_count} lessons (simple query)')
        
        if lessons_count == 0:
            logger.warning('No lessons found after select_related/prefetch_related!')
            logger.warning(f'But raw count shows: {all_lessons_count} lessons')
            logger.warning(f'Database engine: {db_info.get("ENGINE")}, Database name: {db_info.get("NAME")}')
            
            # Try to check if we're using wrong database
            try:
                from lessons.models import VideoFile
                video_count = VideoFile.objects.count()
                logger.info(f'Videos in database: {video_count}')
            except DatabaseError as db_error:
                error_msg = f'Database error while checking videos: {str(db_error)}'
                logger.error(error_msg, exc_info=True)
                return JsonResponse({
                    'lessons': [],
                    'error': 'database_connection_error',
                    'error_message': 'Ошибка подключения к базе данных english_lessons',
                    'error_details': str(db_error),
                    'database': db_name,
                    'message': 'Не удалось подключиться к базе данных. Проверьте настройки подключения.'
                }, status=500)
            except Exception as ve:
                logger.error(f'Error checking videos: {ve}', exc_info=True)
            
            # Если уроки есть, но не возвращаются - это проблема с запросом
            if all_lessons_count > 0:
                logger.error('CRITICAL: Lessons exist but query returns 0! This is a query problem.')
                # Попробуем вернуть уроки без оптимизаций
                try:
                    lessons_fallback = list(Lesson.objects.all().order_by('created_at')[:10])
                    logger.info(f'Fallback query returned {len(lessons_fallback)} lessons')
                    if lessons_fallback:
                        logger.info('Using fallback query results')
                        # Продолжим обработку с fallback данными
                        lessons = Lesson.objects.all().order_by('created_at')
                        lessons_count = len(lessons_fallback)
                    else:
                        # База подключена, но уроков нет
                        return JsonResponse({
                            'lessons': [],
                            'error': 'no_lessons',
                            'message': 'В базе данных нет уроков',
                            'database': db_name,
                            'is_english_lessons': is_english_lessons_db
                        })
                except DatabaseError as db_error:
                    error_msg = f'Database error in fallback query: {str(db_error)}'
                    logger.error(error_msg, exc_info=True)
                    return JsonResponse({
                        'lessons': [],
                        'error': 'database_connection_error',
                        'error_message': 'Ошибка подключения к базе данных english_lessons',
                        'error_details': str(db_error),
                        'database': db_name,
                        'message': 'Не удалось подключиться к базе данных. Проверьте настройки подключения.'
                    }, status=500)
            else:
                # База подключена, но уроков нет
                return JsonResponse({
                    'lessons': [],
                    'error': 'no_lessons',
                    'message': 'В базе данных нет уроков',
                    'database': db_name,
                    'is_english_lessons': is_english_lessons_db
                })
    except DatabaseError as db_error:
        error_msg = f'Database connection error: {str(db_error)}'
        error_trace = traceback.format_exc()
        logger.error(f'{error_msg}\n{error_trace}', exc_info=True)
        return JsonResponse({
            'lessons': [],
            'error': 'database_connection_error',
            'error_message': 'Ошибка подключения к базе данных english_lessons',
            'error_details': str(db_error),
            'database': db_name,
            'message': 'Не удалось подключиться к базе данных. Проверьте настройки подключения.',
            'traceback': error_trace
        }, status=500)
    except Exception as e:
        error_msg = f'Unexpected error fetching lessons: {str(e)}'
        error_trace = traceback.format_exc()
        logger.error(f'{error_msg}\n{error_trace}', exc_info=True)
        return JsonResponse({
            'lessons': [],
            'error': 'system_error',
            'error_message': 'Системная ошибка при загрузке уроков',
            'error_details': str(e),
            'database': db_name,
            'message': f'Произошла ошибка: {str(e)}',
            'traceback': error_trace
        }, status=500)
    
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
    logger.info(f'Processing {lessons_count} lessons for response')
    
    # Используем iterator() для больших наборов данных, чтобы не загружать все в память сразу
    # Это помогает избежать таймаутов при больших объемах данных
    lessons_iter = lessons.iterator(chunk_size=50) if hasattr(lessons, 'iterator') else lessons
    
    for lesson in lessons_iter:
        try:
            # Оптимизация: используем prefetched карточки вместо запроса к БД
            # Если prefetch не сработал, делаем отдельный запрос с ограничением
            try:
                cards = list(lesson.cards.all())
            except Exception as cards_error:
                logger.warning(f'Error loading cards for lesson {lesson.id}: {cards_error}')
                # Fallback: загружаем карточки отдельным запросом
                from lessons.models import ExerciseCard
                cards = list(ExerciseCard.objects.filter(lesson=lesson))
            
            topics = set(card.topic or 'general' for card in cards)
            topics_count = len(topics)
            cards_total = len(cards)
            
            logger.debug(f'Processing lesson {lesson.id}: title="{lesson.title}", cards={cards_total}')
            
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
            stars = 0
            if user_progress and progress_data['cards_total'] > 0:
                user_completed = progress_data['cards_completed'] == progress_data['cards_total']
                logger.debug(
                    f'Lesson {lesson.id}: cards_completed={progress_data["cards_completed"]}, '
                    f'cards_total={progress_data["cards_total"]}, user_completed={user_completed}'
                )
                
                # Получаем звёзды из последней попытки урока
                lesson_attempt = lesson_attempts_map.get(lesson.id)
                if lesson_attempt:
                    stars = lesson_attempt.stars or 0
            
            lesson_data = {
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
                'user_completed': user_completed,  # Добавляем поле для карты
                'stars': stars  # Добавляем звёзды
            }
            lessons_data.append(lesson_data)
            logger.debug(f'Added lesson {lesson.id} to response data')
        except Exception as e:
            logger.error(f'Error processing lesson {lesson.id}: {e}', exc_info=True)
            # Продолжаем обработку других уроков
    
    logger.info(f'Returning {len(lessons_data)} lessons, user_progress={user_progress is not None}')
    
    if len(lessons_data) > 0:
        logger.info(f'First lesson: id={lessons_data[0].get("id")}, title={lessons_data[0].get("title", "N/A")}')
        logger.info(f'Last lesson: id={lessons_data[-1].get("id")}, title={lessons_data[-1].get("title", "N/A")}')
    else:
        logger.warning('lessons_data is empty! This should not happen if lessons exist in database.')
        logger.warning(f'Original lessons_count was: {lessons_count}')
        logger.warning(f'Database: {db_engine}, Name: {db_name}')
        logger.warning(f'Is english_lessons: {is_english_lessons_db}')
        
        # Если подключены к english_lessons, но уроков нет - это нормально
        if is_english_lessons_db:
            logger.info('Connected to english_lessons, but no lessons found - returning no_lessons error')
            return JsonResponse({
                'lessons': [],
                'error': 'no_lessons',
                'message': 'В базе данных нет уроков',
                'database': db_name,
                'is_english_lessons': is_english_lessons_db
            })
        else:
            logger.error(f'NOT connected to english_lessons! Current database: {db_name}')
            return JsonResponse({
                'lessons': [],
                'error': 'wrong_database',
                'error_message': f'Подключены не к той базе данных. Текущая: {db_name}',
                'database': db_name,
                'is_english_lessons': is_english_lessons_db,
                'message': f'Подключены к базе данных "{db_name}", а не к "english_lessons". Проверьте настройки подключения.'
            }, status=500)
    
    try:
        response_data = {'lessons': lessons_data}
        logger.info(f'Response data prepared: {len(response_data["lessons"])} lessons')
        response = JsonResponse(response_data)
        logger.info('✅ JSON response created successfully')
        return response
    except Exception as e:
        logger.error(f'❌ Error creating JSON response: {e}', exc_info=True)
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f'Traceback: {error_trace}')
        return JsonResponse({'error': str(e), 'lessons': [], 'traceback': error_trace}, status=500)


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

