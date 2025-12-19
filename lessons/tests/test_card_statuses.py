"""
Тесты для проверки сохранения и загрузки статусов карточек
"""
from django.test import TestCase, Client
from django.contrib.sessions.middleware import SessionMiddleware
from lessons.models import Lesson, ExerciseCard, UserProgress, LessonAttempt, CardAttempt, VideoFile


class CardStatusTest(TestCase):
    def setUp(self):
        """Создаем тестовые данные"""
        self.client = Client()
        
        # Создаем видео для урока
        from lessons.models import VideoFile
        self.video = VideoFile.objects.create(
            file_path="/test/video.mp4"
        )
        
        # Создаем урок и карточку
        self.lesson = Lesson.objects.create(
            title="Test Lesson",
            description="Test Description",
            language_level="A1",
            video=self.video,
            transcript_text="Test transcript"
        )
        
        self.card = ExerciseCard.objects.create(
            lesson=self.lesson,
            card_type="repeat",
            question_text="Test question",
            prompt_text="Test prompt"
        )
        
        # Создаем сессию
        session = self.client.session
        session.save()
        self.session_key = session.session_key
        
        # Создаем прогресс пользователя
        self.user_progress = UserProgress.objects.create(
            session_key=self.session_key,
            total_experience=0,
            current_level=1
        )
        
        # Создаем попытку урока
        self.lesson_attempt = LessonAttempt.objects.create(
            user_progress=self.user_progress,
            lesson=self.lesson,
            status='in_progress',
            total_cards=1
        )
    
    def test_card_status_saved_and_loaded(self):
        """Тест: статус карточки сохраняется и загружается"""
        # Создаем попытку карточки со статусом 5 (зеленый)
        card_attempt = CardAttempt.objects.create(
            lesson_attempt=self.lesson_attempt,
            card=self.card,
            user_answer="test",
            is_correct=True,
            card_status=5,
            attempts_count=1
        )
        
        # Проверяем, что статус сохранился
        self.assertEqual(card_attempt.card_status, 5)
        self.assertEqual(card_attempt.get_status_color(), 'green')
        
        # Загружаем статусы через API
        response = self.client.get(f'/api/lessons/{self.lesson.id}/card_statuses/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('card_statuses', data)
        self.assertIn(str(self.card.id), data['card_statuses'])
        self.assertEqual(data['card_statuses'][str(self.card.id)]['status'], 5)
        self.assertEqual(data['card_statuses'][str(self.card.id)]['color'], 'green')
    
    def test_card_status_persists_after_refresh(self):
        CardAttempt.objects.create(
            lesson_attempt=self.lesson_attempt,
            card=self.card,
            user_answer="test",
            is_correct=True,
            card_status=5,
            attempts_count=1
        )
        response = self.client.get(f'/api/lessons/{self.lesson.id}/card_statuses/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('card_statuses', data)
        self.assertIn(str(self.card.id), data['card_statuses'])
        self.assertEqual(data['card_statuses'][str(self.card.id)]['status'], 5)


class CardTextCleaningTest(TestCase):
    """Тесты для проверки очистки экранированных кавычек"""
    
    def test_clean_text_removes_escaped_quotes(self):
        from lessons.models import VideoFile
        from lessons.services.card_cleaner import clean_card_data
        
        video = VideoFile.objects.create(
            file_path="/test/video.mp4",
            file_name="test_video.mp4"
        )
        lesson = Lesson.objects.create(
            title="Test Lesson",
            description="Test",
            language_level="A1",
            video=video,
            transcript_text="Test transcript"
        )
        card_data = {
            'questionText': "Learn \\'dog\\'",
            'promptText': 'Test prompt'
        }
        cleaned = clean_card_data(card_data)
        self.assertNotIn("\\'", cleaned['question_text'])
        self.assertIn("dog", cleaned['question_text'])
        self.assertEqual(cleaned['question_text'], "Learn 'dog'")

