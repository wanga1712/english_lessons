import os
import sys
from pathlib import Path

# Add project to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_lessons.settings')

import django
django.setup()

from django.conf import settings
import psycopg2

print("=== PostgreSQL Connection Check ===")
print()

# Check .env file
env_file = BASE_DIR / '.env'
print(f".env file exists: {env_file.exists()}")

if env_file.exists():
    print(f".env file path: {env_file}")
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'DB_HOST' in content:
            print("OK: DB_HOST found in .env")
        if 'DB_NAME' in content:
            print("OK: DB_NAME found in .env")
        if 'DB_USER' in content:
            print("OK: DB_USER found in .env")
        if 'DB_PASSWORD' in content:
            print("OK: DB_PASSWORD found in .env")

print()
print("=== Current Django Database Settings ===")
db = settings.DATABASES['default']
print(f"Engine: {db['ENGINE']}")
print(f"Name: {db['NAME']}")
print(f"User: {db.get('USER', 'N/A')}")
print(f"Host: {db.get('HOST', 'N/A')}")
print(f"Port: {db.get('PORT', 'N/A')}")

print()
print("=== Testing PostgreSQL Connection ===")

try:
    # Try to connect with settings from Django
    if 'postgresql' in db['ENGINE']:
        conn = psycopg2.connect(
            host=db.get('HOST', 'localhost'),
            port=db.get('PORT', '5432'),
            user=db.get('USER', 'postgres'),
            password=db.get('PASSWORD', ''),
            database=db.get('NAME', 'english_lessons'),
            connect_timeout=5
        )
        print("SUCCESS: PostgreSQL connection works!")
        
        cursor = conn.cursor()
        
        # Check lessons
        cursor.execute("SELECT COUNT(*) FROM lessons_lesson")
        lesson_count = cursor.fetchone()[0]
        print(f"Lessons in PostgreSQL: {lesson_count}")
        
        # Check videos
        cursor.execute("SELECT COUNT(*) FROM lessons_videofile")
        video_count = cursor.fetchone()[0]
        print(f"Videos in PostgreSQL: {video_count}")
        
        if lesson_count > 0:
            cursor.execute("SELECT id, title FROM lessons_lesson LIMIT 5")
            lessons = cursor.fetchall()
            print("\nSample lessons:")
            for lesson in lessons:
                print(f"  ID {lesson[0]}: {lesson[1]}")
        
        conn.close()
    else:
        print("WARNING: Django is using SQLite, not PostgreSQL")
        print("This means PostgreSQL connection failed during Django startup")
        
except psycopg2.OperationalError as e:
    print(f"ERROR: PostgreSQL connection FAILED: {e}")
    print("\nPossible reasons:")
    print("1. PostgreSQL server is not running")
    print("2. Wrong connection settings (host, port, user, password)")
    print("3. Database 'english_lessons' does not exist")
    print("4. Firewall blocking connection")
except Exception as e:
    print(f"ERROR: {e}")

