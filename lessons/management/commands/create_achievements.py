"""
Команда для создания базовых достижений
"""
from django.core.management.base import BaseCommand
from lessons.models import Achievement


class Command(BaseCommand):
    help = 'Создает базовые достижения для системы'

    def handle(self, *args, **kwargs):
        achievements_data = [
            {
                'code': 'first_lesson',
                'title': 'Первый урок',
                'description': 'Завершите свой первый урок',
                'emoji': '🎉',
                'requirement_type': 'lessons_completed',
                'requirement_value': 1
            },
            {
                'code': 'five_lessons',
                'title': '5 уроков',
                'description': 'Завершите 5 уроков',
                'emoji': '🌟',
                'requirement_type': 'lessons_completed',
                'requirement_value': 5
            },
            {
                'code': 'ten_lessons',
                'title': '10 уроков',
                'description': 'Завершите 10 уроков',
                'emoji': '🏆',
                'requirement_type': 'lessons_completed',
                'requirement_value': 10
            },
            {
                'code': 'level_1_complete',
                'title': 'Уровень 1 завершен',
                'description': 'Завершите 25 уроков',
                'emoji': '🎖️',
                'requirement_type': 'lessons_completed',
                'requirement_value': 25
            },
            {
                'code': 'perfect_score',
                'title': 'Идеальный результат',
                'description': 'Получите 100 баллов',
                'emoji': '💎',
                'requirement_type': 'score',
                'requirement_value': 100
            },
            {
                'code': 'streak_7',
                'title': 'Неделя подряд',
                'description': 'Занимайтесь 7 дней подряд',
                'emoji': '🔥',
                'requirement_type': 'streak_days',
                'requirement_value': 7
            },
            {
                'code': 'streak_30',
                'title': 'Месяц подряд',
                'description': 'Занимайтесь 30 дней подряд',
                'emoji': '⚡',
                'requirement_type': 'streak_days',
                'requirement_value': 30
            },
            {
                'code': 'all_topics',
                'title': 'Всезнайка',
                'description': 'Пройдите все темы',
                'emoji': '🧠',
                'requirement_type': 'all_topics',
                'requirement_value': 1
            },
        ]

        created_count = 0
        for ach_data in achievements_data:
            achievement, created = Achievement.objects.get_or_create(
                code=ach_data['code'],
                defaults=ach_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Создано достижение: {achievement.emoji} {achievement.title}')
                )
            else:
                self.stdout.write(f'Достижение уже существует: {achievement.emoji} {achievement.title}')

        self.stdout.write(
            self.style.SUCCESS(f'\nВсего создано {created_count} новых достижений')
        )

