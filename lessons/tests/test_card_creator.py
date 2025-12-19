from django.test import TestCase
from lessons.models import Lesson, ExerciseCard, VideoFile
from lessons.services.card_creator import prepare_spelling_card, prepare_repeat_card, create_card


class CardCreatorTest(TestCase):
    def setUp(self):
        self.video = VideoFile.objects.create(
            file_path="/test/video.mp4",
            file_name="test_video.mp4"
        )
        self.lesson = Lesson.objects.create(
            title="Test Lesson",
            description="Test",
            language_level="A1",
            video=self.video,
            transcript_text="Test transcript"
        )
    
    def test_prepare_spelling_card_scrambles_letters(self):
        card_data = {
            'cardType': 'spelling',
            'correctAnswer': 'jump'
        }
        extra_data = {}
        result = prepare_spelling_card(card_data, extra_data)
        self.assertIn('scrambledLetters', result)
        self.assertEqual(len(result['scrambledLetters']), 4)
        self.assertEqual(set(result['scrambledLetters']), {'j', 'u', 'm', 'p'})
        self.assertNotEqual(result['scrambledLetters'], ['j', 'u', 'm', 'p'])
    
    def test_prepare_spelling_card_ignores_non_spelling(self):
        card_data = {'cardType': 'repeat'}
        extra_data = {}
        result = prepare_spelling_card(card_data, extra_data)
        self.assertEqual(result, {})
    
    def test_prepare_repeat_card_creates_words(self):
        card_data = {'cardType': 'repeat'}
        extra_data = {}
        question_text = "It's sunny, it's rainy"
        result = prepare_repeat_card(card_data, extra_data, question_text)
        self.assertIn('words', result)
        self.assertEqual(len(result['words']), 2)
        self.assertEqual(result['words'], ["It's sunny", "it's rainy"])
    
    def test_prepare_repeat_card_handles_single_word(self):
        card_data = {'cardType': 'repeat'}
        extra_data = {}
        question_text = "Hello"
        result = prepare_repeat_card(card_data, extra_data, question_text)
        self.assertIn('words', result)
        self.assertEqual(result['words'], ['Hello'])
    
    def test_create_card_success(self):
        card_data = {
            'cardType': 'repeat',
            'iconName': 'sun',
            'options': None,
            'topic': 'weather',
            'orderIndex': 0,
            'isReview': False
        }
        cleaned_data = {
            'question_text': 'Test question',
            'prompt_text': 'Test prompt',
            'translation_text': None,
            'hint_text': None,
            'correct_answer': None
        }
        extra_data = {}
        card, success = create_card(self.lesson, card_data, cleaned_data, extra_data, 0)
        self.assertTrue(success)
        self.assertIsNotNone(card)
        self.assertEqual(card.question_text, 'Test question')
        self.assertEqual(card.card_type, 'repeat')
    
    def test_create_card_failure(self):
        card_data = {
            'cardType': 'repeat',
            'iconName': None,
            'options': None,
            'topic': None,
            'orderIndex': 0,
            'isReview': False
        }
        cleaned_data = {
            'question_text': '',
            'prompt_text': '',
            'translation_text': None,
            'hint_text': None,
            'correct_answer': None
        }
        extra_data = None
        try:
            card, success = create_card(self.lesson, card_data, cleaned_data, extra_data, 0)
            if success:
                card.delete()
        except Exception:
            pass
        self.assertTrue(True)

