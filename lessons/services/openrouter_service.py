import json
import logging
import re
import sys
import time
import requests
from django.conf import settings
from lessons.services.prompts import (
    get_system_prompt,
    get_user_prompt_with_repetition,
    get_analysis_system_prompt,
    get_analysis_user_prompt,
    get_card_generation_system_prompt,
    get_card_generation_user_prompt
)
from lessons.services.ai_client import AIClient
from lessons.services.json_parser import clean_ai_response, try_fix_json_errors, try_fix_truncated_json

logger = logging.getLogger(__name__)


class OpenRouterService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.api_url = settings.OPENROUTER_API_URL
        self.client = AIClient(self.api_key, self.model, self.api_url)
    
    def analyze_lesson_two_stage(self, transcript_text, previous_lessons_info=None):
        """
        Двухэтапный анализ урока через OpenRouter AI
        
        Этап 1: Анализ транскрипта и определение темы + план карточек
        Этап 2: Формирование карточек по готовому плану
        
        Args:
            transcript_text: Транскрибированный текст урока
            previous_lessons_info: Информация о предыдущих уроках
            
        Returns:
            dict: Структурированные данные урока с карточками
        """
        logger.info('')
        logger.info('=' * 80)
        logger.info('🚀 ДВУХЭТАПНЫЙ ПРОЦЕСС ОБРАБОТКИ УРОКА')
        logger.info('=' * 80)
        sys.stdout.flush()
        
        # ============================================================
        # ЭТАП 1: АНАЛИЗ ТРАНСКРИПТА И ПЛАНИРОВАНИЕ
        # ============================================================
        logger.info('')
        logger.info('📋 ЭТАП 1: АНАЛИЗ ТРАНСКРИПТА И ПЛАНИРОВАНИЕ КАРТОЧЕК')
        logger.info('─' * 80)
        logger.info('⏳ Отправка запроса в первую модель для анализа...')
        sys.stdout.flush()
        
        try:
            analysis_result = self._analyze_transcript(transcript_text, previous_lessons_info)
            logger.info('✅ Анализ завершён успешно!')
            logger.info(f'   Название урока: {analysis_result.get("lessonTitle")}')
            logger.info(f'   Найдено тем: {len(analysis_result.get("topics", []))}')
            sys.stdout.flush()
        except Exception as e:
            logger.error(f'❌ ОШИБКА на этапе анализа: {str(e)}', exc_info=True)
            sys.stdout.flush()
            raise
        
        # ============================================================
        # ЭТАП 2: ФОРМИРОВАНИЕ КАРТОЧЕК ДЛЯ КАЖДОЙ ТЕМЫ
        # ============================================================
        logger.info('')
        logger.info('🎴 ЭТАП 2: ФОРМИРОВАНИЕ КАРТОЧЕК ПО ПЛАНУ')
        logger.info('─' * 80)
        
        all_cards = []
        topics_data = []
        
        for topic_info in analysis_result.get('topics', []):
            topic_id = topic_info.get('topic')
            topic_name = topic_info.get('topicName', topic_id)
            
            logger.info(f'⏳ Создание карточек для темы "{topic_name}" ({topic_id})...')
            sys.stdout.flush()
            
            try:
                topic_cards = self._generate_cards_for_topic(topic_info, transcript_text)
                
                # Добавляем topic к каждой карточке
                for card in topic_cards:
                    card['topic'] = topic_id
                
                all_cards.extend(topic_cards)
                
                topics_data.append({
                    'topic': topic_id,
                    'topicName': topic_name,
                    'cards': topic_cards
                })
                
                logger.info(f'✅ Создано {len(topic_cards)} карточек для темы "{topic_name}"')
                sys.stdout.flush()
                
            except Exception as e:
                logger.error(f'❌ ОШИБКА создания карточек для темы "{topic_name}": {str(e)}', exc_info=True)
                sys.stdout.flush()
                # Продолжаем с другими темами
                continue
        
        if not all_cards:
            raise ValueError('Не удалось создать ни одной карточки для урока')
        
        # Формируем итоговый результат
        lesson_data = {
            'lessonTitle': analysis_result.get('lessonTitle', 'Untitled Lesson'),
            'lessonDescription': analysis_result.get('lessonDescription', ''),
            'languageLevel': analysis_result.get('languageLevel', 'A1'),
            'topics': topics_data,
            'cards': all_cards,
            '_raw_content': None,  # Для двухэтапного процесса не сохраняем сырой ответ
            '_two_stage': True  # Флаг, что использовался двухэтапный процесс
        }
        
        logger.info('')
        logger.info('=' * 80)
        logger.info('✅ ДВУХЭТАПНЫЙ ПРОЦЕСС ЗАВЕРШЁН УСПЕШНО!')
        logger.info(f'   Урок: {lesson_data["lessonTitle"]}')
        logger.info(f'   Тем: {len(topics_data)}')
        logger.info(f'   Всего карточек: {len(all_cards)}')
        logger.info('=' * 80)
        sys.stdout.flush()
        
        return lesson_data
    
    def _analyze_transcript(self, transcript_text, previous_lessons_info=None):
        system_prompt = get_analysis_system_prompt()
        user_prompt = get_analysis_user_prompt(transcript_text, previous_lessons_info)
        analysis_data = self.client.analyze_transcript(system_prompt, user_prompt)
        logger.info(f'Анализ распарсен: {len(analysis_data.get("topics", []))} тем')
        sys.stdout.flush()
        return analysis_data
    
    def _generate_cards_for_topic(self, topic_info, transcript_text):
        system_prompt = get_card_generation_system_prompt()
        user_prompt = get_card_generation_user_prompt(topic_info, transcript_text)
        cards = self.client.generate_cards(system_prompt, user_prompt)
        expected_count = sum(topic_info.get('cardPlan', {}).values())
        if len(cards) < expected_count:
            logger.warning(f'Создано {len(cards)} карточек вместо {expected_count} для темы "{topic_info.get("topic")}"')
            sys.stdout.flush()
        return cards
    
    def analyze_lesson(self, transcript_text, previous_lessons_info=None):
        """
        Анализ урока через OpenRouter AI
        
        Args:
            transcript_text: Транскрибированный текст урока
            previous_lessons_info: Информация о предыдущих уроках для включения в промпт
            
        Returns:
            dict: Структурированные данные урока с карточками
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:8000',
            'X-Title': 'English Lessons App'
        }
        
        payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'system',
                        'content': get_system_prompt()
                    },
                    {
                        'role': 'user',
                        'content': get_user_prompt_with_repetition(transcript_text, previous_lessons_info)
                    }
                ],
                'temperature': 0.7,
                'max_tokens': 16000,  # Увеличено для поддержки нескольких тем и больших ответов (было 12000)
            }
        
        try:
            logger.info('Отправка запроса к OpenRouter AI...')
            sys.stdout.flush()
            
            # Увеличиваем timeout для больших ответов
            try:
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=180)
                response.raise_for_status()
            except requests.exceptions.Timeout:
                logger.error('❌ Таймаут запроса к OpenRouter AI (180 сек)')
                raise Exception('Таймаут запроса к OpenRouter AI. Попробуйте позже.')
            except requests.exceptions.ConnectionError as e:
                logger.error(f'❌ Ошибка соединения с OpenRouter AI: {str(e)}')
                raise Exception(f'Ошибка соединения с OpenRouter AI: {str(e)}')
            except requests.exceptions.ChunkedEncodingError as e:
                logger.error(f'❌ Ответ от OpenRouter AI оборвался: {str(e)}')
                raise Exception(f'Ответ от OpenRouter AI оборвался. Попробуйте еще раз.')
            
            result = response.json()
            original_content = result['choices'][0]['message']['content']
            
            # Проверяем, не обрезан ли ответ
            finish_reason = result['choices'][0].get('finish_reason', '')
            if finish_reason == 'length':
                logger.warning('⚠️ ВНИМАНИЕ: Ответ от ИИ был обрезан из-за превышения max_tokens!')
                logger.warning('   Запрашиваю продолжение ответа...')
                sys.stdout.flush()
                continuation = self.client._request_continuation(original_content, 'lesson')
                original_content = original_content + continuation
                logger.info(f'✅ Получено продолжение, общая длина: {len(original_content)} символов')
                sys.stdout.flush()
            
            logger.info('✅ Получен ответ от OpenRouter AI, длина: %s символов', len(original_content))
            logger.info('   Первые 200 символов: %s', original_content[:200])
            logger.info('   Finish reason: %s', finish_reason)
            sys.stdout.flush()
            
            # Сохраняем оригинальный ответ для отладки
            content = original_content
            
            logger.info('⏳ Очистка ответа от markdown и комментариев...')
            sys.stdout.flush()
            content = clean_ai_response(content)
            logger.info('✅ Ответ очищен, длина после очистки: %s символов', len(content))
            sys.stdout.flush()
            
            # Парсим JSON с детальной обработкой ошибок
            logger.info('⏳ Парсинг JSON ответа...')
            sys.stdout.flush()
            
            try:
                lesson_data = json.loads(content)
                logger.info('✅ JSON успешно распарсен')
                sys.stdout.flush()
            except json.JSONDecodeError as json_error:
                # Пытаемся найти и исправить распространённые проблемы
                logger.warning(f'⚠️ Первая попытка парсинга не удалась: {json_error}. Пытаюсь исправить...')
                sys.stdout.flush()
                
                error_pos = getattr(json_error, 'pos', len(content))
                fixed_content = try_fix_json_errors(content, error_pos)
                try:
                    lesson_data = json.loads(fixed_content)
                    logger.info('✅ JSON успешно исправлен и распарсен')
                    sys.stdout.flush()
                except json.JSONDecodeError:
                    logger.error('❌ Не удалось исправить JSON')
                    sys.stdout.flush()
                    raise json_error

            # Если модель вернула только sections, но не cards — разворачиваем все карточки в общий список
            if 'cards' not in lesson_data and 'sections' in lesson_data:
                logger.info('В ответе найдены sections, но нет cards — формируем общий список карточек')
                all_cards = []
                order_index = 0
                for section in lesson_data.get('sections', []):
                    for card in section.get('cards', []):
                        if 'orderIndex' not in card:
                            card['orderIndex'] = order_index
                        all_cards.append(card)
                        order_index += 1
                lesson_data['cards'] = all_cards

            # Валидация структуры
            if 'lessonTitle' not in lesson_data:
                logger.error('❌ В ответе от ИИ отсутствует lessonTitle')
                logger.error(f'   Ключи в ответе: {list(lesson_data.keys())}')
                logger.error(f'   Первые 500 символов ответа: {content[:500]}')
                sys.stdout.flush()
                raise ValueError('Неверная структура ответа от ИИ модели: отсутствует lessonTitle')
            
            # Проверяем наличие карточек
            cards_count = len(lesson_data.get('cards', []))
            topics_count = len(lesson_data.get('topics', []))
            
            if cards_count == 0 and topics_count == 0:
                logger.error('❌ В ответе от ИИ нет карточек и нет тем!')
                logger.error(f'   lesson_data keys: {list(lesson_data.keys())}')
                logger.error(f'   lessonTitle: {lesson_data.get("lessonTitle")}')
                logger.error(f'   Полный lesson_data: {lesson_data}')
                sys.stdout.flush()
                raise ValueError('Неверная структура ответа от ИИ модели: нет карточек и нет тем')
            
            # Если есть topics, но нет cards на верхнем уровне - это нормально, мы соберём их из topics
            if topics_count > 0:
                total_cards_in_topics = sum(len(topic.get('cards', [])) for topic in lesson_data.get('topics', []))
                logger.info(f'✅ Найдено {topics_count} тем с {total_cards_in_topics} карточками')
                
                # Проверяем, что в каждой теме есть карточки
                for topic_idx, topic in enumerate(lesson_data.get('topics', [])):
                    topic_cards = topic.get('cards', [])
                    if not topic_cards:
                        logger.error(f'❌ Тема {topic_idx + 1} "{topic.get("topic", "unknown")}" не содержит карточек!')
                        logger.error(f'   Данные темы: {topic}')
                    else:
                        # Проверяем первую карточку на наличие обязательных полей
                        first_card = topic_cards[0] if topic_cards else {}
                        if not first_card.get('questionText'):
                            logger.error(f'❌ Первая карточка темы "{topic.get("topic")}" не имеет questionText!')
                            logger.error(f'   Данные карточки: {first_card}')
                sys.stdout.flush()
            else:
                logger.info(f'✅ Найдено {cards_count} карточек на верхнем уровне')
                
                # Проверяем первую карточку на наличие обязательных полей
                if cards_count > 0:
                    first_card = lesson_data.get('cards', [])[0]
                    if not first_card.get('questionText'):
                        logger.error(f'❌ Первая карточка не имеет questionText!')
                        logger.error(f'   Данные карточки: {first_card}')
                        sys.stdout.flush()

            # Сохраняем сырой ответ
            lesson_data['_raw_content'] = content

            logger.info(
                '✅ Успешно распарсен ответ: тема="%s", карточек=%s, тем=%s',
                lesson_data.get('lessonTitle'),
                cards_count,
                topics_count,
            )

            return lesson_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f'Ошибка запроса к OpenRouter AI: {str(e)}', exc_info=True)
            raise Exception(f'Ошибка запроса к OpenRouter AI: {str(e)}')
        except json.JSONDecodeError as e:
            # Детальное логирование для отладки
            error_pos = getattr(e, 'pos', None)
            error_line = getattr(e, 'lineno', None)
            error_col = getattr(e, 'colno', None)
            
            logger.error(f'Ошибка парсинга JSON от OpenRouter AI: {str(e)}', exc_info=True)
            
            # Показываем контекст вокруг ошибки
            if error_pos is not None:
                start = max(0, error_pos - 200)
                end = min(len(content), error_pos + 200)
                context = content[start:end]
                logger.error(f'Контекст ошибки (позиция {error_pos}, строка {error_line}, колонка {error_col}):\n{context}')
            
            # Сохраняем полный ответ в файл для отладки
            try:
                import os
                debug_dir = os.path.join(settings.BASE_DIR, 'debug_responses')
                os.makedirs(debug_dir, exist_ok=True)
                debug_file = os.path.join(debug_dir, f'ai_response_error_{int(time.time())}.txt')
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write('=== ОРИГИНАЛЬНЫЙ ОТВЕТ ===\n')
                    f.write(original_content)
                    f.write('\n\n=== ПОСЛЕ ОЧИСТКИ ===\n')
                    f.write(content)
                    f.write(f'\n\n=== ОШИБКА ===\n')
                    f.write(str(e))
                    if error_pos is not None:
                        f.write(f'\n\nПозиция ошибки: {error_pos}, строка {error_line}, колонка {error_col}')
                logger.error(f'Полный ответ сохранён в файл: {debug_file}')
            except Exception as save_error:
                logger.error(f'Не удалось сохранить ответ для отладки: {save_error}')
            
            # Показываем начало и конец ответа
            logger.error(f'Начало ответа (первые 1000 символов):\n{content[:1000]}')
            logger.error(f'Конец ответа (последние 1000 символов):\n{content[-1000:]}')
            
            # Пытаемся найти и исправить проблему вокруг ошибки
            if error_pos is not None:
                start = max(0, error_pos - 100)
                end = min(len(content), error_pos + 100)
                error_context = content[start:end]
                logger.error(f'Контекст вокруг ошибки (позиция {error_pos}):\n{error_context}')
                
                logger.info('🔄 Попытка автоматического исправления JSON...')
                sys.stdout.flush()
                fixed_content = try_fix_json_errors(content, error_pos)
                try:
                    lesson_data = json.loads(fixed_content)
                    logger.info('✅ JSON успешно исправлен автоматически!')
                    sys.stdout.flush()
                    return lesson_data
                except Exception as fix_error:
                    logger.error(f'❌ Автоматическое исправление не помогло: {fix_error}')
                    sys.stdout.flush()
            
            raise Exception(f'Ошибка парсинга JSON от OpenRouter AI: {str(e)}. Позиция ошибки: строка {error_line}, колонка {error_col}')
        except Exception as e:
            logger.error(f'Неожиданная ошибка при работе с OpenRouter AI: {str(e)}', exc_info=True)
            raise
    
