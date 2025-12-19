from django.db import models
from django.utils import timezone


class VideoFile(models.Model):
    """Модель для хранения информации о видеофайлах"""
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('processing', 'Обрабатывается'),
        ('done', 'Обработано'),
        ('error', 'Ошибка'),
    ]
    
    file_path = models.CharField(max_length=500, unique=True, verbose_name='Путь к файлу')
    file_name = models.CharField(max_length=255, verbose_name='Имя файла')
    file_size = models.BigIntegerField(null=True, blank=True, verbose_name='Размер файла (байт)')
    transcript_path = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='Путь к файлу транскрипта',
    )
    has_transcript = models.BooleanField(
        default=False,
        verbose_name='Транскрипт сохранён',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата обработки')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    error_message = models.TextField(null=True, blank=True, verbose_name='Сообщение об ошибке')
    processing_status = models.CharField(
        max_length=50,
        default='idle',
        verbose_name='Статус обработки',
        help_text='idle, transcribing, generating_lesson, done, error'
    )
    processing_message = models.TextField(
        null=True,
        blank=True,
        verbose_name='Сообщение об обработке'
    )
    
    class Meta:
        verbose_name = 'Видеофайл'
        verbose_name_plural = 'Видеофайлы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.file_name} ({self.status})'


class Lesson(models.Model):
    """Модель урока английского языка"""
    
    LANGUAGE_LEVEL_CHOICES = [
        ('A0', 'A0 - Начальный'),
        ('A1', 'A1 - Элементарный'),
        ('A2', 'A2 - Ниже среднего'),
        ('B1', 'B1 - Средний'),
        ('B2', 'B2 - Выше среднего'),
    ]
    
    video = models.OneToOneField(
        VideoFile,
        on_delete=models.CASCADE,
        related_name='lesson',
        verbose_name='Видеофайл'
    )
    title = models.CharField(max_length=200, verbose_name='Название урока')
    description = models.TextField(blank=True, verbose_name='Описание')
    transcript_text = models.TextField(verbose_name='Транскрипт урока')
    raw_ai_response = models.TextField(
        null=True,
        blank=True,
        verbose_name='Сырой ответ ИИ (JSON)',
    )
    language_level = models.CharField(
        max_length=10,
        choices=LANGUAGE_LEVEL_CHOICES,
        default='A1',
        verbose_name='Уровень языка'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.title} ({self.language_level})'


class ExerciseCard(models.Model):
    """Модель карточки с упражнением"""
    
    CARD_TYPE_CHOICES = [
        ('repeat', 'Повторить'),
        ('translate', 'Перевести'),
        ('choose', 'Выбрать вариант'),
        ('color', 'Цвет'),
        ('speak', 'Проговорить'),
        ('match', 'Сопоставить'),
        ('spelling', 'Написание'),
        ('new_words', 'Новые слова'),
        ('writing', 'Письмо'),
    ]
    
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='cards',
        verbose_name='Урок'
    )
    card_type = models.CharField(
        max_length=20,
        choices=CARD_TYPE_CHOICES,
        verbose_name='Тип карточки'
    )
    question_text = models.TextField(verbose_name='Текст вопроса')
    prompt_text = models.TextField(verbose_name='Инструкция для ребёнка')
    correct_answer = models.TextField(null=True, blank=True, verbose_name='Правильный ответ')
    options = models.JSONField(null=True, blank=True, verbose_name='Варианты ответов')
    extra_data = models.JSONField(null=True, blank=True, verbose_name='Дополнительные данные')
    order_index = models.IntegerField(default=0, verbose_name='Порядок отображения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Карточка упражнения'
        verbose_name_plural = 'Карточки упражнений'
        ordering = ['lesson', 'order_index']
    
    # Поля для изображений и визуальных элементов
    image_url = models.URLField(null=True, blank=True, verbose_name='URL изображения')
    icon_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Название иконки/пиктограммы',
        help_text='Название иконки из библиотеки (например: sun, cloud, dog, cat)'
    )
    translation_text = models.TextField(
        null=True,
        blank=True,
        verbose_name='Перевод для показа после правильного ответа'
    )
    hint_text = models.TextField(
        null=True,
        blank=True,
        verbose_name='Текст подсказки',
        help_text='Показывается после нескольких неправильных попыток'
    )
    topic = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Тема карточки',
        help_text='Тема урока, к которой относится карточка (например: weather, actions, colors)'
    )
    is_repetition_card = models.BooleanField(
        default=False,
        verbose_name='Карточка для повторения',
        help_text='Отмечено, если карточка создана для повторения из предыдущих уроков'
    )
    
    def __str__(self):
        return f'{self.lesson.title} - {self.get_card_type_display()} (#{self.order_index})'


class UserProgress(models.Model):
    """Модель для отслеживания общего прогресса пользователя"""
    
    # Используем session_key как идентификатор пользователя (можно заменить на User если будет авторизация)
    session_key = models.CharField(
        max_length=40,
        unique=True,
        verbose_name='Ключ сессии пользователя'
    )
    total_experience = models.IntegerField(default=0, verbose_name='Общий опыт')
    current_level = models.IntegerField(default=1, verbose_name='Текущий уровень')
    total_cards_completed = models.IntegerField(default=0, verbose_name='Всего карточек пройдено')
    total_lessons_completed = models.IntegerField(default=0, verbose_name='Всего уроков пройдено')
    correct_answers_count = models.IntegerField(default=0, verbose_name='Правильных ответов')
    incorrect_answers_count = models.IntegerField(default=0, verbose_name='Неправильных ответов')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Прогресс пользователя'
        verbose_name_plural = 'Прогресс пользователей'
        ordering = ['-total_experience']
    
    def __str__(self):
        return f'Уровень {self.current_level} (Опыт: {self.total_experience})'
    
    def calculate_level(self):
        """Вычисляет уровень на основе опыта"""
        # Формула: каждый уровень требует 100 * level опыта
        # Уровень 1: 0-99, Уровень 2: 100-299, Уровень 3: 300-599 и т.д.
        level = 1
        exp_needed = 0
        while self.total_experience >= exp_needed:
            level += 1
            exp_needed += 100 * level
        return max(1, level - 1)
    
    def add_experience(self, amount):
        """Добавляет опыт и обновляет уровень"""
        self.total_experience += amount
        new_level = self.calculate_level()
        if new_level > self.current_level:
            self.current_level = new_level
        self.save()


class LessonAttempt(models.Model):
    """Модель попытки прохождения урока"""
    
    STATUS_CHOICES = [
        ('in_progress', 'В процессе'),
        ('completed', 'Завершено'),
        ('abandoned', 'Прервано'),
    ]
    
    user_progress = models.ForeignKey(
        UserProgress,
        on_delete=models.CASCADE,
        related_name='lesson_attempts',
        verbose_name='Прогресс пользователя'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Урок'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
        verbose_name='Статус'
    )
    score = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Оценка (0-100)',
        help_text='Процент правильных ответов'
    )
    stars = models.IntegerField(
        default=0,
        verbose_name='Звёзды',
        help_text='Количество звёзд: 1★ = 50-69%, 2★ = 70-99%, 3★ = 100%'
    )
    correct_cards = models.IntegerField(default=0, verbose_name='Правильных карточек')
    total_cards = models.IntegerField(default=0, verbose_name='Всего карточек')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Начато')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Завершено')
    
    class Meta:
        verbose_name = 'Попытка прохождения урока'
        verbose_name_plural = 'Попытки прохождения уроков'
        ordering = ['-started_at']
    
    def __str__(self):
        return f'{self.lesson.title} - {self.get_status_display()} ({self.score}%)'
    
    def calculate_score(self):
        """Вычисляет оценку на основе правильных ответов"""
        if self.total_cards == 0:
            return 0
        self.score = (self.correct_cards / self.total_cards) * 100
        self.save()
        return self.score
    
    def calculate_stars(self):
        """Рассчитать количество звёзд: 1★ = 50-69%, 2★ = 70-99%, 3★ = 100%"""
        if not self.score:
            self.calculate_score()
        
        if self.score >= 100:
            return 3
        elif self.score >= 70:
            return 2
        elif self.score >= 50:
            return 1
        else:
            return 0
    
    def update_stars(self):
        """Обновить звёзды при завершении попытки"""
        self.stars = self.calculate_stars()
        self.save()


class CardAttempt(models.Model):
    """Модель попытки ответа на карточку"""
    
    lesson_attempt = models.ForeignKey(
        LessonAttempt,
        on_delete=models.CASCADE,
        related_name='card_attempts',
        verbose_name='Попытка урока'
    )
    card = models.ForeignKey(
        ExerciseCard,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Карточка'
    )
    user_answer = models.TextField(null=True, blank=True, verbose_name='Ответ пользователя')
    is_correct = models.BooleanField(verbose_name='Правильный ответ')
    attempts_count = models.IntegerField(default=1, verbose_name='Количество попыток')
    hint_shown = models.BooleanField(default=False, verbose_name='Показана подсказка')
    experience_gained = models.IntegerField(default=0, verbose_name='Получено опыта')
    card_status = models.IntegerField(
        default=0,
        verbose_name='Статус карточки',
        help_text='0=красный (не пройдено), 3=желтый (с ошибками), 5=зеленый (идеально)'
    )
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name='Время ответа')
    
    class Meta:
        verbose_name = 'Попытка ответа на карточку'
        verbose_name_plural = 'Попытки ответов на карточки'
        ordering = ['answered_at']
    
    def __str__(self):
        status = '✓' if self.is_correct else '✗'
        return f'{status} {self.card.question_text[:50]}... ({self.attempts_count} попыток)'
    
    def get_status_color(self):
        """Возвращает цвет статуса"""
        if self.card_status == 0:
            return 'red'
        elif self.card_status == 3:
            return 'yellow'
        elif self.card_status == 5:
            return 'green'
        return 'gray'


class UserAvatar(models.Model):
    """Модель персонажа пользователя"""
    
    user_progress = models.OneToOneField(
        UserProgress,
        on_delete=models.CASCADE,
        related_name='avatar',
        verbose_name='Прогресс пользователя'
    )
    avatar_name = models.CharField(
        max_length=100,
        default='Ученик',
        verbose_name='Имя персонажа'
    )
    avatar_emoji = models.CharField(
        max_length=10,
        default='🎓',
        verbose_name='Эмодзи персонажа'
    )
    total_score = models.FloatField(
        default=0.0,
        verbose_name='Средний балл',
        help_text='Средний балл по всем карточкам (0-5)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Персонаж пользователя'
        verbose_name_plural = 'Персонажи пользователей'
        ordering = ['-total_score']
    
    def __str__(self):
        return f'{self.avatar_name} ({self.avatar_emoji}) - Балл: {self.total_score:.1f}'
    
    def update_score(self):
        """Обновляет средний балл на основе всех карточек пользователя
        
        Формула: сумма баллов всех карточек с ненулевым статусом / количество таких карточек
        Красный (0) не учитывается в расчете
        """
        # Получаем все попытки пользователя
        lesson_attempts = LessonAttempt.objects.filter(user_progress=self.user_progress)
        
        # Получаем все карточки с ненулевым статусом (не равные 0)
        card_attempts = CardAttempt.objects.filter(
            lesson_attempt__in=lesson_attempts
        ).exclude(card_status=0)
        
        if card_attempts.exists():
            # Суммируем баллы и делим на количество
            total_points = sum(ca.card_status for ca in card_attempts)
            count = card_attempts.count()
            self.total_score = total_points / count if count > 0 else 0.0
        else:
            self.total_score = 0.0
        
        self.save()
        return self.total_score


class Achievement(models.Model):
    """Модель для достижений (badges)"""
    
    code = models.CharField(max_length=50, unique=True, verbose_name='Код достижения')
    title = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    emoji = models.CharField(max_length=10, verbose_name='Эмодзи')
    requirement_type = models.CharField(
        max_length=50,
        verbose_name='Тип требования',
        help_text='lessons_completed, perfect_score, streak_days, etc.'
    )
    requirement_value = models.IntegerField(
        default=1,
        verbose_name='Значение требования'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'
        ordering = ['requirement_value']
    
    def __str__(self):
        return f'{self.emoji} {self.title}'


class UserAchievement(models.Model):
    """Модель для связи пользователей и достижений"""
    
    user_progress = models.ForeignKey(
        UserProgress,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name='Прогресс пользователя'
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        verbose_name='Достижение'
    )
    unlocked_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата разблокировки')
    
    class Meta:
        verbose_name = 'Достижение пользователя'
        verbose_name_plural = 'Достижения пользователей'
        unique_together = ['user_progress', 'achievement']
        ordering = ['-unlocked_at']
    
    def __str__(self):
        return f'{self.user_progress} - {self.achievement}'