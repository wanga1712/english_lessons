from django.test import TestCase
from lessons.services.card_cleaner import clean_text, clean_card_data


class CardCleanerTest(TestCase):
    def test_clean_text_removes_escaped_quotes(self):
        self.assertEqual(clean_text("Learn \\'dog\\'"), "Learn 'dog'")
        self.assertEqual(clean_text('Learn \\"cat\\"'), 'Learn "cat"')
        self.assertEqual(clean_text("Learn &#39;bird&#39;"), "Learn 'bird'")
        self.assertEqual(clean_text('Learn &quot;fish&quot;'), 'Learn "fish"')
        self.assertEqual(clean_text("Learn &apos;dog&apos;"), "Learn 'dog'")
    
    def test_clean_text_handles_none(self):
        self.assertIsNone(clean_text(None))
        self.assertIsNone(clean_text(''))
    
    def test_clean_text_handles_double_escaping(self):
        self.assertEqual(clean_text("Learn \\\\'dog\\\\'"), "Learn 'dog'")
        self.assertEqual(clean_text('Learn \\\\"cat\\\\"'), 'Learn "cat"')
    
    def test_clean_card_data_cleans_all_fields(self):
        card_data = {
            'questionText': "Learn \\'dog\\'",
            'promptText': 'Say \\"hello\\"',
            'translationText': "It&#39;s a dog",
            'hintText': 'Think &quot;animal&quot;',
            'correctAnswer': "It\\'s correct"
        }
        result = clean_card_data(card_data)
        self.assertEqual(result['question_text'], "Learn 'dog'")
        self.assertEqual(result['prompt_text'], 'Say "hello"')
        self.assertEqual(result['translation_text'], "It's a dog")
        self.assertEqual(result['hint_text'], 'Think "animal"')
        self.assertEqual(result['correct_answer'], "It's correct")
    
    def test_clean_card_data_handles_missing_fields(self):
        card_data = {
            'questionText': 'Test'
        }
        result = clean_card_data(card_data)
        self.assertEqual(result['question_text'], 'Test')
        self.assertEqual(result['prompt_text'], '')
        self.assertIsNone(result['translation_text'])
        self.assertIsNone(result['hint_text'])
        self.assertIsNone(result['correct_answer'])

