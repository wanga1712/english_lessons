import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_lessons.settings')

import django
django.setup()

from lessons.models import Lesson
from django.conf import settings

print("=== Checking Database Connection ===")
db = settings.DATABASES['default']
print(f"Database engine: {db['ENGINE']}")
print(f"Database name: {db['NAME']}")
print()

print("=== Checking Lessons ===")
count = Lesson.objects.count()
print(f"Total lessons in database: {count}")

if count > 0:
    print("\nFirst 5 lessons:")
    lessons = Lesson.objects.all()[:5]
    for lesson in lessons:
        cards_count = lesson.cards.count()
        print(f"  ID {lesson.id}: {lesson.title} ({cards_count} cards)")
else:
    print("No lessons found in database!")

