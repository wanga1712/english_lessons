from django.contrib import admin
from lessons.models import (
    VideoFile, Lesson, ExerciseCard,
    UserProgress, LessonAttempt, CardAttempt, UserAvatar
)


@admin.register(VideoFile)
class VideoFileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'status', 'created_at', 'processed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('file_name', 'file_path')
    readonly_fields = ('created_at', 'processed_at', 'file_size')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('file_path', 'file_name', 'file_size')
        }),
        ('Статус', {
            'fields': ('status', 'error_message')
        }),
        ('Даты', {
            'fields': ('created_at', 'processed_at')
        }),
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'language_level', 'video', 'created_at')
    list_filter = ('language_level', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'raw_ai_response')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('video', 'title', 'description', 'language_level')
        }),
        ('Контент', {
            'fields': ('transcript_text', 'raw_ai_response')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ExerciseCard)
class ExerciseCardAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'card_type', 'order_index', 'question_text')
    list_filter = ('card_type', 'lesson')
    search_fields = ('question_text', 'prompt_text')
    ordering = ('lesson', 'order_index')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('lesson', 'card_type', 'order_index')
        }),
        ('Контент карточки', {
            'fields': ('question_text', 'prompt_text', 'correct_answer')
        }),
        ('Дополнительные данные', {
            'fields': ('options', 'extra_data', 'image_url', 'icon_name')
        }),
        ('Подсказки и переводы', {
            'fields': ('translation_text', 'hint_text')
        }),
    )


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'current_level', 'total_experience', 'total_lessons_completed', 'updated_at')
    list_filter = ('current_level', 'created_at')
    search_fields = ('session_key',)
    readonly_fields = ('created_at', 'updated_at', 'current_level')
    ordering = ('-total_experience',)


@admin.register(LessonAttempt)
class LessonAttemptAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'user_progress', 'status', 'score', 'correct_cards', 'total_cards', 'started_at')
    list_filter = ('status', 'started_at')
    search_fields = ('lesson__title', 'user_progress__session_key')
    readonly_fields = ('started_at', 'completed_at', 'score')
    ordering = ('-started_at',)


@admin.register(CardAttempt)
class CardAttemptAdmin(admin.ModelAdmin):
    list_display = ('card', 'lesson_attempt', 'is_correct', 'card_status', 'attempts_count', 'experience_gained', 'answered_at')
    list_filter = ('is_correct', 'card_status', 'hint_shown', 'answered_at')
    search_fields = ('card__question_text', 'user_answer')
    readonly_fields = ('answered_at',)
    ordering = ('-answered_at',)


@admin.register(UserAvatar)
class UserAvatarAdmin(admin.ModelAdmin):
    list_display = ('avatar_name', 'user_progress', 'avatar_emoji', 'total_score', 'updated_at')
    list_filter = ('total_score', 'created_at')
    search_fields = ('avatar_name', 'user_progress__session_key')
    readonly_fields = ('created_at', 'updated_at', 'total_score')
    ordering = ('-total_score',)
