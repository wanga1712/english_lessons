import os
import sys
import logging
from django.conf import settings
from django.utils import timezone
from lessons.models import VideoFile, Lesson
from lessons.services.transcription_service import TranscriptionService
from lessons.services.openrouter_service import OpenRouterService
from lessons.services.repetition_service import RepetitionService
from lessons.services.card_cleaner import clean_card_data
from lessons.services.card_creator import prepare_spelling_card, prepare_repeat_card, create_card

logger = logging.getLogger(__name__)


class VideoProcessor:
    def __init__(self):
        self.transcription_service = TranscriptionService()
        self.openrouter_service = OpenRouterService()
        self.repetition_service = RepetitionService()
    
    def process_video(self, video_file, force_recreate=False):
        if video_file.status == 'processing' and not force_recreate:
            logger.warning(f'Видео {video_file.id} уже обрабатывается')
            try:
                existing_lesson = Lesson.objects.get(video=video_file)
                return existing_lesson
            except Lesson.DoesNotExist:
                return None
        if video_file.status == 'done' and hasattr(video_file, 'lesson') and not force_recreate:
            logger.warning(f'Урок для видео {video_file.id} уже существует')
            return video_file.lesson
        logger.info('=' * 80)
        logger.info(f'НАЧАЛО ОБРАБОТКИ ВИДЕО: {video_file.file_name} (ID: {video_file.id})')
        logger.info('=' * 80)
        sys.stdout.flush()
        video_file.status = 'processing'
        video_file.processing_status = 'transcribing'
        video_file.processing_message = 'Транскрипция видео...'
        video_file.save()
        try:
            transcript_text = self.transcription_service.transcribe(video_file.file_path)
            if not transcript_text or len(transcript_text.strip()) < 50:
                raise ValueError(f'Транскрипт слишком короткий или пустой: {len(transcript_text) if transcript_text else 0} символов')
            video_file.has_transcript = True
            video_file.processing_status = 'generating_lesson'
            video_file.processing_message = 'Генерация урока с помощью ИИ...'
            video_file.save()
            logger.info('')
            logger.info('=' * 80)
            logger.info('ГЕНЕРАЦИЯ УРОКА С ПОМОЩЬЮ ИИ')
            logger.info('=' * 80)
            logger.info(f'Длина транскрипта: {len(transcript_text)} символов')
            sys.stdout.flush()
            previous_lessons_info = self._get_previous_lessons_info()
            use_two_stage = getattr(settings, 'USE_TWO_STAGE_PROCESS', True)
            if use_two_stage:
                logger.info('Используется двухэтапный процесс генерации урока')
                sys.stdout.flush()
                lesson_data = self.openrouter_service.analyze_lesson_two_stage(transcript_text, previous_lessons_info)
            else:
                logger.info('Используется одноэтапный процесс генерации урока')
                sys.stdout.flush()
                try:
                    lesson_data = self.openrouter_service.analyze_lesson_two_stage(transcript_text, previous_lessons_info)
                except Exception as e:
                    logger.warning(f'Двухэтапный процесс не удался: {e}. Пробуем одноэтапный...')
                    sys.stdout.flush()
                    lesson_data = self.openrouter_service.analyze_lesson(transcript_text, previous_lessons_info)
            filtered_text = self._filter_transcript(transcript_text)
            lesson = self._create_lesson_from_ai_response(video_file, filtered_text, lesson_data, force_recreate)
            video_file.status = 'done'
            video_file.processing_status = 'done'
            video_file.processing_message = f'Урок создан: {lesson.title}'
            video_file.processed_at = timezone.now()
            video_file.save()
            
            # Удаляем видеофайл после успешной обработки для экономии места
            try:
                if os.path.exists(video_file.file_path):
                    file_size_mb = os.path.getsize(video_file.file_path) / (1024 * 1024)
                    os.remove(video_file.file_path)
                    logger.info(f'✅ Видеофайл удален: {video_file.file_path} ({file_size_mb:.2f} MB)')
                else:
                    logger.warning(f'⚠️ Видеофайл не найден для удаления: {video_file.file_path}')
            except Exception as e:
                logger.error(f'❌ Ошибка при удалении видеофайла {video_file.file_path}: {str(e)}')
                # Не прерываем выполнение, так как урок уже создан
            
            logger.info('')
            logger.info('=' * 80)
            logger.info('ОБРАБОТКА ВИДЕО ЗАВЕРШЕНА УСПЕШНО!')
            logger.info(f'Урок ID: {lesson.id}')
            logger.info(f'Название: {lesson.title}')
            logger.info(f'Карточек: {lesson.cards.count()}')
            logger.info('=' * 80)
            logger.info('')
            sys.stdout.flush()
            return lesson
        except Exception as e:
            logger.error(f'Ошибка обработки видео {video_file.id}: {str(e)}', exc_info=True)
            video_file.status = 'error'
            video_file.processing_status = 'error'
            video_file.processing_message = f'Ошибка: {str(e)}'
            video_file.error_message = str(e)
            video_file.save()
            raise
    
    def _filter_transcript(self, text):
        import re
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\.,!?;:\-\'"]', '', text)
        words = text.split()
        filtered_words = [w for w in words if len(w) > 1 or w.isalnum()]
        text = ' '.join(filtered_words)
        return text.strip()
    
    def _get_previous_lessons_info(self):
        previous_lessons = Lesson.objects.all().order_by('-created_at')[:5]
        lessons_info = []
        for lesson in previous_lessons:
            topics = set()
            for card in lesson.cards.all():
                if card.topic:
                    topics.add(card.topic)
            lessons_info.append({
                'title': lesson.title,
                'topics': list(topics),
                'cards_count': lesson.cards.count()
            })
        return lessons_info
    
    def _create_lesson_from_ai_response(self, video_file, transcript_text, lesson_data, force_recreate=False):
        if force_recreate and hasattr(video_file, 'lesson'):
            old_lesson = video_file.lesson
            logger.info(f'Удаление старого урока {old_lesson.id} для пересоздания')
            old_lesson.delete()
        if not force_recreate and hasattr(video_file, 'lesson'):
            logger.warning(f'Урок для видео {video_file.id} уже существует')
            return video_file.lesson
        lesson = Lesson.objects.create(
            video=video_file,
            title=lesson_data.get('lessonTitle', 'Untitled Lesson'),
            description=lesson_data.get('lessonDescription', ''),
            transcript_text=transcript_text,
            language_level=lesson_data.get('languageLevel', 'A1'),
            raw_ai_response=lesson_data.get('_raw_content'),
        )
        cards_data = lesson_data.get('cards', [])
        topics_data = lesson_data.get('topics', [])
        if topics_data:
            all_cards = []
            for topic_data in topics_data:
                topic_id = topic_data.get('topic', '')
                topic_cards = topic_data.get('cards', [])
                for card in topic_cards:
                    card['topic'] = topic_id
                    all_cards.append(card)
            cards_data = all_cards
        if not cards_data:
            logger.error(f'КРИТИЧЕСКАЯ ОШИБКА: Нет карточек для создания урока!')
            logger.error(f'lesson_data keys: {list(lesson_data.keys())}')
            logger.error(f'topics_data: {topics_data}')
            logger.error(f'cards_data (из lesson_data): {lesson_data.get("cards", [])}')
            logger.error(f'lessonTitle: {lesson_data.get("lessonTitle")}')
            sys.stdout.flush()
            raise ValueError(f'Нет карточек для создания урока. Модель должна возвращать карточки согласно промпту.')
        logger.info(f'Создание {len(cards_data)} карточек для урока {lesson.id}...')
        logger.info(f'Урок: {lesson.title}')
        logger.info(f'Видео: {video_file.file_name}')
        sys.stdout.flush()
        
        # Оптимизация: подготавливаем все карточки для bulk создания
        cards_to_create = []
        skipped_cards_count = 0
        
        for index, card_data in enumerate(cards_data):
            if not isinstance(card_data, dict):
                logger.warning(f'Карточка {index} не является словарём: {type(card_data)}')
                skipped_cards_count += 1
                continue
            
            card_type = card_data.get('cardType', 'repeat')
            cleaned_data = clean_card_data(card_data)
            question_text = cleaned_data.get('question_text', '') or ''
            prompt_text = cleaned_data.get('prompt_text', '') or ''
            correct_answer = cleaned_data.get('correct_answer', '') or ''
            has_content = (question_text and question_text.strip()) or (prompt_text and prompt_text.strip()) or (correct_answer and correct_answer.strip())
            
            if not has_content:
                logger.warning(f'Карточка {index} (тип: {card_type}) не имеет контента, пропускаем')
                skipped_cards_count += 1
                continue
            
            if not question_text or not question_text.strip():
                question_text = prompt_text or correct_answer or 'Exercise'
                cleaned_data['question_text'] = question_text
            
            extra_data = card_data.get('extraData') or {}
            extra_data = prepare_spelling_card(card_data, extra_data)
            extra_data = prepare_repeat_card(card_data, extra_data, question_text)
            
            # Подготавливаем объект карточки для bulk создания
            from lessons.models import ExerciseCard
            card_obj = ExerciseCard(
                lesson=lesson,
                card_type=card_data.get('cardType', 'repeat'),
                question_text=cleaned_data['question_text'],
                prompt_text=cleaned_data['prompt_text'],
                correct_answer=cleaned_data['correct_answer'],
                options=card_data.get('options'),
                extra_data=extra_data if extra_data else None,
                icon_name=card_data.get('iconName'),
                translation_text=cleaned_data['translation_text'],
                hint_text=cleaned_data['hint_text'],
                topic=card_data.get('topic'),
                order_index=card_data.get('orderIndex', index),
                is_repetition_card=card_data.get('isReview', False)
            )
            cards_to_create.append(card_obj)
        
        # Оптимизация: bulk создание всех карточек одним запросом
        if cards_to_create:
            ExerciseCard.objects.bulk_create(cards_to_create)
            created_cards_count = len(cards_to_create)
        else:
            created_cards_count = 0
        logger.info(f'Создан урок {lesson.id} с {created_cards_count} карточками (из {len(cards_data)} полученных)')
        if created_cards_count < len(cards_data):
            logger.warning(f'Не все карточки были созданы! Создано: {created_cards_count}, получено: {len(cards_data)}, пропущено: {skipped_cards_count}')
        if created_cards_count == 0:
            logger.error(f'КРИТИЧЕСКАЯ ОШИБКА: Не создано ни одной карточки для урока {lesson.id}!')
            logger.error(f'Это означает, что все карточки были пропущены из-за ошибок')
            sys.stdout.flush()
            raise ValueError(f'Не удалось создать ни одной карточки для урока. Все {len(cards_data)} карточек были пропущены.')
        sys.stdout.flush()
        return lesson
