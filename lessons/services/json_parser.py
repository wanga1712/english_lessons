import json
import re
import logging
from django.conf import settings
import time

logger = logging.getLogger(__name__)


def clean_ai_response(content):
    content = content.strip()
    if content.startswith('```json'):
        content = content[7:]
    elif content.startswith('```'):
        content = content[3:]
    if content.endswith('```'):
        content = content[:-3]
    content = content.strip()
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    first_brace = content.find('{')
    last_brace = content.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        content = content[first_brace:last_brace + 1]
    content = re.sub(r',\s*}', '}', content)
    content = re.sub(r',\s*]', ']', content)
    return content.strip()


def try_fix_truncated_json(content, error_pos):
    try:
        before_error = content[:error_pos]
        last_valid_card_end = before_error.rfind('},')
        if last_valid_card_end == -1:
            last_valid_card_end = before_error.rfind('}')
        if last_valid_card_end > 0:
            card_start = before_error.rfind(',', 0, last_valid_card_end)
            if card_start == -1:
                card_start = before_error.rfind('[', 0, last_valid_card_end)
                if card_start != -1:
                    card_start += 1
            if card_start > 0 and last_valid_card_end > card_start:
                last_card_text = before_error[card_start:last_valid_card_end + 1]
                try:
                    if last_card_text.startswith(','):
                        last_card_text = last_card_text[1:].strip()
                    test_card = json.loads(last_card_text.rstrip(','))
                    open_braces = before_error.count('{') - before_error.count('}')
                    open_brackets = before_error.count('[') - before_error.count(']')
                    fixed = before_error
                    for _ in range(open_brackets):
                        fixed += ']'
                    for _ in range(open_braces):
                        fixed += '}'
                    logger.info(f'Восстановлен обрезанный JSON: закрыто {open_braces} объектов и {open_brackets} массивов')
                    return fixed
                except:
                    pass
        open_braces = before_error.count('{') - before_error.count('}')
        open_brackets = before_error.count('[') - before_error.count(']')
        fixed = before_error
        for _ in range(open_brackets):
            fixed += ']'
        for _ in range(open_braces):
            fixed += '}'
        logger.warning(f'Восстановление через закрытие скобок: закрыто {open_braces} объектов и {open_brackets} массивов')
        return fixed
    except Exception as e:
        logger.error(f'Ошибка при попытке восстановления JSON: {str(e)}')
        return content


def try_fix_json_errors(content, error_pos):
    fixes = [
        (r',(\s*[}\]])', r'\1'),
        (r':\s*"([^"]*?)\n', r': "\1"\n'),
        (r'//.*?$', '', re.MULTILINE),
        (r'/\*.*?\*/', '', re.DOTALL),
        (r':\s*"([^"]*?)$', r': "\1"'),
    ]
    fixed_content = content
    for fix in fixes:
        if len(fix) == 3:
            pattern, replacement, flags = fix
            fixed_content = re.sub(pattern, replacement, fixed_content, flags=flags)
        else:
            pattern, replacement = fix
            fixed_content = re.sub(pattern, replacement, fixed_content, flags=re.MULTILINE | re.DOTALL)
    if error_pos and error_pos > len(content) * 0.85:
        fixed_content = try_fix_truncated_json(fixed_content, error_pos)
    return fixed_content

