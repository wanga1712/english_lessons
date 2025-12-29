"""
Анализ GIF файла для определения структуры спрайтов
"""
from PIL import Image
import os

gif_path = r'C:\Users\wangr\Downloads\6d130ef633b79c8f11dd7cd227c675ba.gif'

if not os.path.exists(gif_path):
    print(f"File not found: {gif_path}")
    exit(1)

gif = Image.open(gif_path)
print(f"Image size: {gif.size}")
print(f"Image mode: {gif.mode}")
print(f"Is animated: {getattr(gif, 'is_animated', False)}")

# Попробуем извлечь все кадры
frames = []
try:
    frame_num = 0
    while True:
        frame = gif.copy()
        frames.append(frame.convert('RGBA'))
        frame_num += 1
        if frame_num >= 100:  # Ограничение для безопасности
            break
        gif.seek(gif.tell() + 1)
except EOFError:
    pass

print(f"Total frames extracted: {len(frames)}")

if len(frames) > 1:
    print(f"Frame 0 size: {frames[0].size}")
    print(f"Frame 1 size: {frames[1].size if len(frames) > 1 else 'N/A'}")
    
    # Проверим, одинаковые ли размеры
    sizes = [f.size for f in frames]
    unique_sizes = set(sizes)
    print(f"Unique frame sizes: {unique_sizes}")
    
    if len(unique_sizes) == 1:
        frame_width, frame_height = frames[0].size
        print(f"\nAll frames are {frame_width}x{frame_height}")
        print(f"Total frames: {len(frames)}")
        
        # Создадим спрайт-лист
        spritesheet_width = frame_width * len(frames)
        spritesheet_height = frame_height
        
        spritesheet = Image.new('RGBA', (spritesheet_width, spritesheet_height), (0, 0, 0, 0))
        
        for i, frame in enumerate(frames):
            x = i * frame_width
            spritesheet.paste(frame, (x, 0))
        
        output_path = 'lessons/static/lessons/img/characters/hero-spritesheet.png'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        spritesheet.save(output_path, 'PNG')
        
        print(f"\nSpritesheet saved: {output_path}")
        print(f"Spritesheet size: {spritesheet_width}x{spritesheet_height}")
        print(f"Frame size: {frame_width}x{frame_height}")
        print(f"Frame count: {len(frames)}")
        
        print(f"\nPhaser code:")
        print(f"this.load.spritesheet('hero', '{{% static \"lessons/img/characters/hero-spritesheet.png\" %}}', {{")
        print(f"  frameWidth: {frame_width},")
        print(f"  frameHeight: {frame_height}")
        print(f"}});")
        print(f"\n// Create animation with {len(frames)} frames")
        print(f"this.anims.create({{")
        print(f"  key: 'hero-idle',")
        print(f"  frames: this.anims.generateFrameNumbers('hero', {{ start: 0, end: {len(frames) - 1} }}),")
        print(f"  frameRate: 10,")
        print(f"  repeat: -1")
        print(f"}});")
else:
    print("Only 1 frame found - might be a static image or spritesheet already")
    # Проверим, может это уже спрайт-лист
    width, height = gif.size
    print(f"\nPossible spritesheet analysis:")
    print(f"  If frames are 64x64: {width // 64} frames horizontally")
    print(f"  If frames are 96x96: {width // 96} frames horizontally")
    print(f"  If frames are 128x128: {width // 128} frames horizontally")

