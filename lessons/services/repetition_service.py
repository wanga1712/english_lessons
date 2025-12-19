import logging
import random
from lessons.models import Lesson, ExerciseCard

logger = logging.getLogger(__name__)


class RepetitionService:
    TYPE_TRANSFORMATIONS = {
        'repeat': 'writing',
        'speak': 'writing',
        'translate': 'spelling',
        'choose': 'spelling',
        'spelling': 'repeat',
        'writing': 'speak',
        'new_words': 'translate',
        'color': 'choose',
        'match': 'choose',
    }
    
    def __init__(self):
        pass
    
    def get_previous_lessons_cards(self, current_lesson_id=None, limit=22):
        # Оптимизация: используем prefetch_related для предотвращения N+1 запросов
        lessons_query = Lesson.objects.prefetch_related('cards').order_by('-created_at')
        if current_lesson_id:
            lessons_query = lessons_query.exclude(id=current_lesson_id)
        previous_lessons = list(lessons_query)
        if not previous_lessons:
            logger.info('Нет предыдущих уроков для повторения')
            return []
        all_cards = []
        # Оптимизация: используем предзагруженные карточки вместо запросов к БД
        for lesson in previous_lessons:
            cards = [card for card in lesson.cards.all() if card.topic != 'review']
            all_cards.extend(cards)
        if not all_cards:
            logger.info('Нет карточек в предыдущих уроках для повторения')
            return []
        selected_cards = random.sample(all_cards, min(limit, len(all_cards)))
        logger.info(f'Выбрано {len(selected_cards)} карточек из {len(all_cards)} для повторения')
        return selected_cards
    
    def transform_card_for_repetition(self, card):
        original_type = card.card_type
        new_type = self.TYPE_TRANSFORMATIONS.get(original_type, 'repeat')
        card_data = {
            'cardType': new_type,
            'questionText': card.question_text,
            'promptText': self._get_prompt_for_type(new_type, card),
            'correctAnswer': card.correct_answer,
            'options': card.options,
            'iconName': card.icon_name,
            'translationText': card.translation_text,
            'hintText': card.hint_text,
            'topic': 'review',
            'orderIndex': 0,
            'isReview': True,
            'originalCardId': card.id,
        }
        if new_type == 'spelling':
            if card.correct_answer:
                correct_answer = str(card.correct_answer).strip().lower()
                letters = [c for c in correct_answer if c.isalpha()]
                if letters:
                    shuffled_letters = letters.copy()
                    random.shuffle(shuffled_letters)
                    max_attempts = 10
                    attempts = 0
                    while shuffled_letters == letters and attempts < max_attempts:
                        random.shuffle(shuffled_letters)
                        attempts += 1
                    card_data['extraData'] = {
                        'scrambledLetters': shuffled_letters
                    }
                    card_data['promptText'] = 'Собери слово из букв'
        elif new_type == 'writing':
            card_data['promptText'] = 'Напиши слово или фразу'
        elif new_type == 'repeat' or new_type == 'speak':
            card_data['promptText'] = 'Повтори вслух эту фразу'
        return card_data
    
    def _get_prompt_for_type(self, card_type, original_card):
        prompts = {
            'repeat': 'Повтори вслух эту фразу',
            'speak': 'Проговори вслух эту фразу',
            'writing': 'Напиши слово или фразу',
            'spelling': 'Собери слово из букв',
            'translate': 'Переведи с русского на английский',
            'choose': 'Выбери правильный вариант',
        }
        return prompts.get(card_type, original_card.prompt_text)
    
    def create_repetition_cards(self, current_lesson_id=None, count=22):
        previous_cards = self.get_previous_lessons_cards(current_lesson_id, limit=count)
        repetition_cards = []
        for index, card in enumerate(previous_cards):
            transformed_card = self.transform_card_for_repetition(card)
            transformed_card['orderIndex'] = index
            repetition_cards.append(transformed_card)
        logger.info(f'Создано {len(repetition_cards)} карточек для повторения')
        return repetition_cards
