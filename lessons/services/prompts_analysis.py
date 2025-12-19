def get_analysis_system_prompt():
    return """
Ты — опытный учитель английского языка для ребёнка 7 лет.
Твоя задача: проанализировать транскрипт урока и определить темы, которые нужно изучить.

Ты НЕ создаёшь карточки, ты только анализируешь и планируешь!

Верни ТОЛЬКО JSON в следующем формате (БЕЗ комментариев и текста вокруг):
{
  "lessonTitle": "Weather, Actions and Colors",
  "lessonDescription": "На уроке мы учили погоду, действия (can/can't) и цвета.",
  "languageLevel": "A1",
  "topics": [
    {
      "topic": "weather",
      "topicName": "Погода",
      "keyWords": ["sunny", "rainy", "cloudy", "windy", "it's"],
      "cardPlan": {
        "repeat": 2,
        "translate": 2,
        "choose": 2,
        "spelling": 2,
        "new_words": 2,
        "writing": 2
      }
    },
    {
      "topic": "actions",
      "topicName": "Действия",
      "keyWords": ["can", "run", "jump", "swim", "I can"],
      "cardPlan": {
        "repeat": 2,
        "translate": 2,
        "choose": 2,
        "spelling": 2,
        "new_words": 2,
        "writing": 2
      }
    }
  ]
}

Обязательные требования:
1. ВНИМАТЕЛЬНО проанализируй транскрипт и определи ВСЕ темы, которые в нём реально упоминаются.
2. НЕ придумывай темы, которых нет в транскрипте.
3. Для каждой темы укажи ключевые слова/фразы, которые встречаются в транскрипте.
4. Для каждой темы создай план карточек (cardPlan) - сколько карточек каждого типа нужно создать.
   Сумма должна быть 12 карточек на тему.
5. lessonTitle - 2-4 слова на английском.
6. lessonDescription - 1-3 предложения на русском, что делал ребёнок на уроке.
"""


def get_analysis_user_prompt(transcript_text, previous_lessons_info=None):
    repetition_section = ""
    if previous_lessons_info and len(previous_lessons_info) > 0:
        lessons_text = "\n".join([
            f"- {info['title']}: темы {', '.join(info['topics'])}, {info['cards_count']} карточек"
            for info in previous_lessons_info[:5]
        ])
        repetition_section = f"""

ВАЖНО: У ребёнка уже есть пройденные уроки:
{lessons_text}

Система автоматически добавит карточки для повторения из предыдущих уроков.
Ты должен определить ТОЛЬКО новые темы из текущего транскрипта.
"""
    
    return f"""Вот полный транскрипт урока на английском языке:

<TRANSCRIPT>
{transcript_text}
</TRANSCRIPT>
{repetition_section}

Проанализируй транскрипт и определи:
1. Какие темы урока упоминаются в транскрипте?
2. Какие ключевые слова/фразы относятся к каждой теме?
3. План карточек для каждой темы (12 карточек на тему).

Верни только валидный JSON без дополнительного текста."""

