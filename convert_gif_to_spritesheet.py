"""
Скрипт для конвертации GIF в спрайт-лист для Phaser
Использование: python convert_gif_to_spritesheet.py
"""
from PIL import Image
import os
import sys

def gif_to_spritesheet(gif_path, output_dir='lessons/static/lessons/img/characters'):
    """
    Конвертирует GIF в спрайт-лист (PNG) для Phaser
    
    Args:
        gif_path: Путь к GIF файлу
        output_dir: Директория для сохранения результата
    """
    try:
        # Открываем GIF
        gif = Image.open(gif_path)
        
        # Получаем информацию о GIF
        frames = []
        frame_count = 0
        
        print(f"[INFO] Открыт GIF: {gif_path}")
        print(f"[INFO] Размер: {gif.size}")
        
        # Извлекаем все кадры
        try:
            while True:
                # Конвертируем в RGBA для поддержки прозрачности
                frame = gif.convert('RGBA')
                frames.append(frame.copy())
                frame_count += 1
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        
        print(f"[INFO] Найдено кадров: {frame_count}")
        
        if frame_count == 0:
            print("[ERROR] Ошибка: GIF не содержит кадров")
            return
        
        # Определяем размер спрайт-листа
        frame_width, frame_height = frames[0].size
        
        # Создаем спрайт-лист (все кадры в один ряд)
        spritesheet_width = frame_width * frame_count
        spritesheet_height = frame_height
        
        spritesheet = Image.new('RGBA', (spritesheet_width, spritesheet_height), (0, 0, 0, 0))
        
        # Размещаем кадры в спрайт-листе
        for i, frame in enumerate(frames):
            x = i * frame_width
            spritesheet.paste(frame, (x, 0))
        
        # Создаем директорию если её нет
        os.makedirs(output_dir, exist_ok=True)
        
        # Сохраняем спрайт-лист
        output_path = os.path.join(output_dir, 'hero-spritesheet.png')
        spritesheet.save(output_path, 'PNG')
        
        print(f"[SUCCESS] Спрайт-лист сохранен: {output_path}")
        print(f"[INFO] Размер спрайт-листа: {spritesheet_width}x{spritesheet_height}")
        print(f"[INFO] Размер одного кадра: {frame_width}x{frame_height}")
        print(f"[INFO] Количество кадров: {frame_count}")
        
        return {
            'path': output_path,
            'frame_width': frame_width,
            'frame_height': frame_height,
            'frame_count': frame_count
        }
        
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    # Путь к GIF файлу
    gif_path = r'C:\Users\wangr\Downloads\6d130ef633b79c8f11dd7cd227c675ba.gif'
    
    if not os.path.exists(gif_path):
        print(f"[ERROR] Файл не найден: {gif_path}")
        print("[INFO] Укажите правильный путь к GIF файлу")
        sys.exit(1)
    
    result = gif_to_spritesheet(gif_path)
    
    if result:
        print("\n" + "="*50)
        print("[SUCCESS] Конвертация завершена успешно!")
        print("="*50)
        print("\n[INFO] Код для Phaser:")
        code_template = f"""
// В preload()
this.load.spritesheet('hero', '{{% static "lessons/img/characters/hero-spritesheet.png" %}}', {{
  frameWidth: {result['frame_width']},
  frameHeight: {result['frame_height']}
}});

// В create() - создать анимацию
this.anims.create({{
  key: 'hero-idle',
  frames: this.anims.generateFrameNumbers('hero', {{ start: 0, end: {result['frame_count'] - 1} }}),
  frameRate: 10,
  repeat: -1
}});

// Использовать
const hero = this.add.sprite(x, y, 'hero');
hero.play('hero-idle');
hero.setOrigin(0.5, 1); // Якорь внизу
hero.setDepth(15);
        """
        print(code_template)
    else:
        print("\n[ERROR] Конвертация не удалась")

