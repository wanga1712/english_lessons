from django.test import TestCase
from lessons.services.json_parser import clean_ai_response, try_fix_truncated_json, try_fix_json_errors


class JsonParserTest(TestCase):
    def test_clean_ai_response_removes_markdown(self):
        content = '```json\n{"test": "value"}\n```'
        result = clean_ai_response(content)
        self.assertEqual(result, '{"test": "value"}')
    
    def test_clean_ai_response_removes_comments(self):
        content = '{"test": "value"} // comment'
        result = clean_ai_response(content)
        self.assertNotIn('//', result)
    
    def test_clean_ai_response_removes_trailing_commas(self):
        content = '{"test": "value",}'
        result = clean_ai_response(content)
        self.assertNotIn(',}', result)
    
    def test_try_fix_truncated_json_closes_braces(self):
        content = '{"cards": [{"id": 1}'
        result = try_fix_truncated_json(content, len(content))
        self.assertIn('}', result)
        self.assertIn(']', result)
    
    def test_try_fix_json_errors_fixes_trailing_commas(self):
        content = '{"test": "value",}'
        result = try_fix_json_errors(content, len(content) - 1)
        self.assertNotIn(',}', result)
    
    def test_try_fix_json_errors_removes_comments(self):
        content = '{"test": "value"} // comment'
        result = try_fix_json_errors(content, len(content))
        self.assertNotIn('//', result)

