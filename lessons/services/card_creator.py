import random
import logging
from lessons.models import ExerciseCard

logger = logging.getLogger(__name__)


def prepare_spelling_card(card_data, extra_data):
    if card_data.get('cardType') == 'spelling' and card_data.get('correctAnswer'):
        correct_answer = str(card_data.get('correctAnswer', '')).strip().lower()
        if correct_answer:
            letters = [c for c in correct_answer if c.isalpha()]
            if letters:
                shuffled_letters = letters.copy()
                random.shuffle(shuffled_letters)
                max_attempts = 10
                attempts = 0
                while shuffled_letters == letters and attempts < max_attempts:
                    random.shuffle(shuffled_letters)
                    attempts += 1
                extra_data['scrambledLetters'] = shuffled_letters
    return extra_data


def prepare_repeat_card(card_data, extra_data, question_text):
    if card_data.get('cardType') == 'repeat':
        if 'words' not in extra_data or not extra_data.get('words'):
            if question_text:
                words = [w.strip() for w in question_text.split(',') if w.strip()]
                if not words:
                    words = [question_text.strip()]
                extra_data['words'] = words
    return extra_data


def create_card(lesson, card_data, cleaned_data, extra_data, index):
    try:
        card = ExerciseCard.objects.create(
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
        return card, True
    except Exception as e:
        logger.error(f'Ошибка создания карточки {index}: {str(e)}', exc_info=True)
        return None, False

