import json
import logging
import sys
import requests
from django.conf import settings
from lessons.services.json_parser import clean_ai_response, try_fix_json_errors, try_fix_truncated_json

logger = logging.getLogger(__name__)


class AIClient:
    def __init__(self, api_key, model, api_url):
        self.api_key = api_key
        self.model = model
        self.api_url = api_url
        if not self.api_key:
            raise ValueError('OPENROUTER_API_KEY не установлен в настройках')
    
    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:8000',
            'X-Title': 'English Lessons App'
        }
    
    def _make_request(self, messages, max_tokens=16000, temperature=0.7, timeout=120):
        headers = self._get_headers()
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
        }
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    
    def analyze_transcript(self, system_prompt, user_prompt):
        try:
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]
            result = self._make_request(messages, max_tokens=4000, timeout=60)
            content = result['choices'][0]['message']['content']
            finish_reason = result['choices'][0].get('finish_reason', '')
            if finish_reason == 'length':
                logger.warning('⚠️ Ответ был обрезан! Запрашиваю продолжение...')
                continuation = self._request_continuation(content, 'analysis')
                content = content + continuation
            content = clean_ai_response(content)
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                fixed_content = try_fix_json_errors(content, getattr(e, 'pos', len(content)))
                return json.loads(fixed_content)
        except Exception as e:
            logger.error(f'Ошибка анализа транскрипта: {str(e)}', exc_info=True)
            raise
    
    def generate_cards(self, system_prompt, user_prompt):
        try:
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]
            result = self._make_request(messages, max_tokens=6000, timeout=120)
            content = result['choices'][0]['message']['content']
            finish_reason = result['choices'][0].get('finish_reason', '')
            if finish_reason == 'length':
                logger.warning('⚠️ Ответ был обрезан! Запрашиваю продолжение...')
                continuation = self._request_continuation(content, 'cards')
                content = content + continuation
            content = clean_ai_response(content)
            try:
                cards_data = json.loads(content)
                return cards_data.get('cards', [])
            except json.JSONDecodeError as e:
                fixed_content = try_fix_truncated_json(content, getattr(e, 'pos', len(content)))
                cards_data = json.loads(fixed_content)
                return cards_data.get('cards', [])
        except Exception as e:
            logger.error(f'Ошибка генерации карточек: {str(e)}', exc_info=True)
            raise
    
    def _request_continuation(self, truncated_content, content_type='json'):
        continuation_prompt = f"""Продолжи и заверши этот незавершенный JSON. 
Важно: верни ТОЛЬКО продолжение, начиная с того места, где текст обрывается.
Не повторяй уже написанное, только продолжение до закрытия всех скобок и массивов.

Незавершенный JSON:
{truncated_content[-500:]}

Продолжение:"""
        try:
            messages = [
                {'role': 'system', 'content': 'Ты помощник, который завершает незавершенный JSON. Возвращай только продолжение текста, без повторения уже написанного.'},
                {'role': 'user', 'content': continuation_prompt}
            ]
            result = self._make_request(messages, max_tokens=4000, timeout=60)
            continuation = result['choices'][0]['message']['content']
            finish_reason = result['choices'][0].get('finish_reason', '')
            if finish_reason == 'length':
                logger.warning('⚠️ Продолжение тоже обрезано! Запрашиваю еще раз...')
                continuation += self._request_continuation(truncated_content + continuation, content_type)
            logger.info(f'✅ Получено продолжение, длина: {len(continuation)} символов')
            return continuation
        except Exception as e:
            logger.error(f'Ошибка при запросе продолжения: {str(e)}', exc_info=True)
            return ''

