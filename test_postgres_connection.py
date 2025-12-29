import os
import sys
from pathlib import Path

# Load .env manually
env_file = Path('.env')
if env_file.exists():
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

print("=== Testing PostgreSQL Connection ===")
print(f"DB_HOST: {os.getenv('DB_HOST', 'localhost')}")
print(f"DB_PORT: {os.getenv('DB_PORT', '5432')}")
print(f"DB_USER: {os.getenv('DB_USER', 'postgres')}")
print(f"DB_NAME: {os.getenv('DB_NAME', 'english_lessons')}")
print(f"DB_PASSWORD: {'*' * len(os.getenv('DB_PASSWORD', ''))}")
print()

try:
    import psycopg2
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'english_lessons'),
        connect_timeout=5
    )
    print("SUCCESS: Connected to PostgreSQL!")
    
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
    
except psycopg2.OperationalError as e:
    print(f"ERROR: Cannot connect to PostgreSQL: {e}")
    print("\nPossible solutions:")
    print("1. Check if PostgreSQL server is running")
    print("2. Check connection settings in .env file")
    print("3. Check firewall settings")
    print("4. Try connecting from DBeaver to verify settings")
except ImportError:
    print("ERROR: psycopg2 not installed")
except Exception as e:
    print(f"ERROR: {e}")

