import logging

logger = logging.getLogger(__name__)


def clean_text(text):
    if not text:
        return None
    cleaned = str(text)
    cleaned = cleaned.replace("\\\\'", "'")
    cleaned = cleaned.replace('\\\\"', '"')
    cleaned = cleaned.replace("\\'", "'")
    cleaned = cleaned.replace('\\"', '"')
    cleaned = cleaned.replace("&#39;", "'")
    cleaned = cleaned.replace("&apos;", "'")
    cleaned = cleaned.replace("&quot;", '"')
    cleaned = cleaned.strip()
    return cleaned if cleaned else None


def clean_card_data(card_data):
    question_text_raw = card_data.get('questionText') or card_data.get('question_text') or ''
    question_text = clean_text(question_text_raw) if question_text_raw else ''
    if question_text is None:
        question_text = ''
    
    prompt_text_raw = card_data.get('promptText') or card_data.get('prompt_text') or ''
    prompt_text = clean_text(prompt_text_raw) if prompt_text_raw else ''
    if prompt_text is None:
        prompt_text = ''
    
    translation_text = clean_text(card_data.get('translationText') or card_data.get('translation_text'))
    hint_text = clean_text(card_data.get('hintText') or card_data.get('hint_text'))
    correct_answer = clean_text(card_data.get('correctAnswer') or card_data.get('correct_answer'))
    
    return {
        'question_text': question_text,
        'prompt_text': prompt_text,
        'translation_text': translation_text,
        'hint_text': hint_text,
        'correct_answer': correct_answer
    }

