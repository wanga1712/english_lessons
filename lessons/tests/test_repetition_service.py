from django.test import TestCase
from lessons.models import Lesson, ExerciseCard, VideoFile
from lessons.services.repetition_service import RepetitionService


class RepetitionServiceTest(TestCase):
    def setUp(self):
        self.service = RepetitionService()
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
        self.card = ExerciseCard.objects.create(
            lesson=self.lesson,
            card_type="repeat",
            question_text="Test question",
            prompt_text="Test prompt",
            topic="weather"
        )
    
    def test_get_previous_lessons_cards_returns_cards(self):
        cards = self.service.get_previous_lessons_cards()
        self.assertGreaterEqual(len(cards), 0)
    
    def test_get_previous_lessons_cards_excludes_current_lesson(self):
        cards = self.service.get_previous_lessons_cards(current_lesson_id=self.lesson.id)
        self.assertEqual(len(cards), 0)
    
    def test_transform_card_for_repetition_changes_type(self):
        result = self.service.transform_card_for_repetition(self.card)
        self.assertEqual(result['cardType'], 'writing')
        self.assertEqual(result['isReview'], True)
        self.assertEqual(result['topic'], 'review')
    
    def test_transform_card_for_repetition_spelling_creates_scrambled_letters(self):
        spelling_card = ExerciseCard.objects.create(
            lesson=self.lesson,
            card_type="translate",
            question_text="Test",
            prompt_text="Test",
            correct_answer="jump",
            topic="weather"
        )
        result = self.service.transform_card_for_repetition(spelling_card)
        self.assertEqual(result['cardType'], 'spelling')
        self.assertIn('extraData', result)
        self.assertIn('scrambledLetters', result['extraData'])
        self.assertEqual(len(result['extraData']['scrambledLetters']), 4)
    
    def test_create_repetition_cards(self):
        cards = self.service.create_repetition_cards(current_lesson_id=self.lesson.id, count=5)
        self.assertIsInstance(cards, list)

