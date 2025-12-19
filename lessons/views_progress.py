"""
Views для работы с прогрессом пользователя
Размер: ~150 строк
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from lessons.models import UserProgress, LessonAttempt, CardAttempt, Lesson, ExerciseCard, UserAvatar

logger = logging.getLogger(__name__)


def _get_or_create_user_progress(request):
    """Получить или создать прогресс пользователя на основе сессии"""
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    user_progress, created = UserProgress.objects.get_or_create(
        session_key=session_key,
        defaults={'total_experience': 0, 'current_level': 1}
    )
    return user_progress


@csrf_exempt
@require_http_methods(['GET'])
def get_user_progress(request):
    """Получить прогресс текущего пользователя"""
    try:
        user_progress = _get_or_create_user_progress(request)
        
        return JsonResponse({
            'total_experience': user_progress.total_experience,
            'current_level': user_progress.current_level,
            'total_cards_completed': user_progress.total_cards_completed,
            'total_lessons_completed': user_progress.total_lessons_completed,
            'correct_answers_count': user_progress.correct_answers_count,
            'incorrect_answers_count': user_progress.incorrect_answers_count,
            'accuracy': (
                round(user_progress.correct_answers_count / 
                      (user_progress.correct_answers_count + user_progress.incorrect_answers_count) * 100, 1)
                if (user_progress.correct_answers_count + user_progress.incorrect_answers_count) > 0
                else 0
            )
        })
    except Exception as e:
        logger.error(f'Ошибка получения прогресса: {str(e)}', exc_info=True)
        return JsonResponse({'error': f'Ошибка: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def start_lesson_attempt(request, lesson_id):
    """Начать попытку прохождения урока"""
    try:
        lesson = Lesson.objects.get(id=lesson_id)
        user_progress = _get_or_create_user_progress(request)
        
        lesson_attempt = LessonAttempt.objects.create(
            user_progress=user_progress,
            lesson=lesson,
            status='in_progress',
            total_cards=lesson.cards.count()
        )
        
        return JsonResponse({
            'attempt_id': lesson_attempt.id,
            'total_cards': lesson_attempt.total_cards,
            'message': 'Попытка начата'
        })
    except Lesson.DoesNotExist:
        return JsonResponse({'error': 'Урок не найден'}, status=404)
    except Exception as e:
        logger.error(f'Ошибка начала урока: {str(e)}', exc_info=True)
        return JsonResponse({'error': f'Ошибка: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def submit_card_answer(request):
    """Отправить ответ на карточку"""
    try:
        data = json.loads(request.body)
        
        attempt_id = data.get('attempt_id')
        card_id = data.get('card_id')
        user_answer = data.get('answer', '')
        is_correct = data.get('is_correct', False)
        
        lesson_attempt = LessonAttempt.objects.get(id=attempt_id)
        card = ExerciseCard.objects.get(id=card_id)
        
        existing_attempt = CardAttempt.objects.filter(
            lesson_attempt=lesson_attempt,
            card=card
        ).first()
        
        if existing_attempt:
            previous_status = existing_attempt.card_status
            existing_attempt.attempts_count += 1
            existing_attempt.user_answer = user_answer
            existing_attempt.is_correct = is_correct
            card_attempt = existing_attempt
        else:
            previous_status = 0
            card_attempt = CardAttempt.objects.create(
                lesson_attempt=lesson_attempt,
                card=card,
                user_answer=user_answer,
                is_correct=is_correct,
                attempts_count=1
            )
        
        # Устанавливаем статус карточки: 0=красный, 3=желтый, 5=зеленый
        # Логика пересдачи: если карточка была желтой (3) и пересдана правильно - становится зеленой (5)
        if is_correct:
            if card_attempt.attempts_count == 1:
                # Первая попытка - идеально
                card_attempt.card_status = 5  # Зеленый - идеально с первой попытки
                experience = 20
            elif previous_status == 3:
                # Пересдача желтой карточки - если правильно, становится зеленой
                card_attempt.card_status = 5  # Зеленый - пересдано до идеального
                experience = 15  # Меньше опыта за пересдачу, но все равно хорошо
            else:
                # Правильно, но не с первой попытки и не пересдача желтой
                card_attempt.card_status = 3  # Желтый - с ошибками
                experience = 10 if card_attempt.attempts_count == 2 else 5
            
            card_attempt.experience_gained = experience
            card_attempt.save()
            
            if not existing_attempt or not existing_attempt.is_correct:
                lesson_attempt.correct_cards += 1
                lesson_attempt.save()
            
            user_progress = lesson_attempt.user_progress
            user_progress.add_experience(experience)
            user_progress.correct_answers_count += 1
            user_progress.total_cards_completed += 1
            user_progress.save()
        else:
            card_attempt.card_status = 0  # Красный - неправильно
            card_attempt.save()
            
            user_progress = lesson_attempt.user_progress
            user_progress.incorrect_answers_count += 1
            user_progress.save()
            
            if card_attempt.attempts_count >= 2 and not card_attempt.hint_shown:
                card_attempt.hint_shown = True
                card_attempt.save()
        
        # Обновляем средний балл персонажа
        user_progress = lesson_attempt.user_progress
        avatar, created = UserAvatar.objects.get_or_create(user_progress=user_progress)
        avatar.update_score()
        
        show_hint = card_attempt.hint_shown and card.hint_text
        
        response_data = {
            'is_correct': is_correct,
            'attempts_count': card_attempt.attempts_count,
            'card_status': card_attempt.card_status,
            'status_color': card_attempt.get_status_color(),
            'experience_gained': card_attempt.experience_gained if is_correct else 0,
            'show_hint': show_hint,
            'hint_text': card.hint_text if show_hint else None,
            'translation_text': card.translation_text if is_correct else None,
            'total_experience': user_progress.total_experience,
            'current_level': user_progress.current_level,
            'avatar_score': avatar.total_score
        }
        
        return JsonResponse(response_data)
        
    except (LessonAttempt.DoesNotExist, ExerciseCard.DoesNotExist) as e:
        return JsonResponse({'error': 'Попытка или карточка не найдены'}, status=404)
    except Exception as e:
        logger.error(f'Ошибка отправки ответа: {str(e)}', exc_info=True)
        return JsonResponse({'error': f'Ошибка: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def complete_lesson_attempt(request, attempt_id):
    """Завершить попытку прохождения урока"""
    try:
        lesson_attempt = LessonAttempt.objects.get(id=attempt_id)
        
        lesson_attempt.status = 'completed'
        lesson_attempt.completed_at = timezone.now()
        lesson_attempt.calculate_score()
        
        user_progress = lesson_attempt.user_progress
        if lesson_attempt.score and lesson_attempt.score >= 70:
            user_progress.total_lessons_completed += 1
            user_progress.save()
        
        return JsonResponse({
            'score': lesson_attempt.score,
            'correct_cards': lesson_attempt.correct_cards,
            'total_cards': lesson_attempt.total_cards,
            'message': 'Урок завершен'
        })
    except LessonAttempt.DoesNotExist:
        return JsonResponse({'error': 'Попытка не найдена'}, status=404)
    except Exception as e:
        logger.error(f'Ошибка завершения урока: {str(e)}', exc_info=True)
        return JsonResponse({'error': f'Ошибка: {str(e)}'}, status=500)

