"""
Визуальный анализ спрайт-листа - сохранение отдельных кадров для проверки
"""
from PIL import Image
import os

spritesheet_path = 'lessons/static/lessons/img/characters/hero-spritesheet.png'
output_dir = 'spritesheet_analysis'

if not os.path.exists(spritesheet_path):
    print(f"File not found: {spritesheet_path}")
    exit(1)

img = Image.open(spritesheet_path)
width, height = img.size

print(f"Spritesheet size: {width}x{height}")
print(f"Creating visual analysis in '{output_dir}' directory...")

os.makedirs(output_dir, exist_ok=True)

# Попробуем разные варианты размеров кадров
test_configs = [
    (100, 353, "5_frames_horizontal"),
    (125, 353, "4_frames_horizontal"),
    (166, 353, "3_frames_horizontal"),
    (250, 353, "2_frames_horizontal"),
    (500, 353, "1_frame_full"),
    (64, 64, "grid_7x5"),
    (100, 100, "grid_5x3"),
    (125, 117, "grid_4x3"),
]

for fw, fh, name in test_configs:
    cols = width // fw
    rows = height // fh
    
    if cols > 0 and rows > 0:
        config_dir = os.path.join(output_dir, name)
        os.makedirs(config_dir, exist_ok=True)
        
        print(f"\nTesting: {fw}x{fh} -> {cols}x{rows} grid")
        
        frame_num = 0
        for row in range(rows):
            for col in range(cols):
                x = col * fw
                y = row * fh
                
                # Извлекаем кадр
                frame = img.crop((x, y, x + fw, y + fh))
                
                # Сохраняем
                frame_path = os.path.join(config_dir, f"frame_{frame_num:02d}.png")
                frame.save(frame_path)
                
                frame_num += 1
        
        print(f"  Saved {frame_num} frames to {config_dir}/")
        print(f"  Check frame_00.png to frame_{frame_num-1:02d}.png")

print(f"\n✅ Analysis complete!")
print(f"📁 Check '{output_dir}' folder to see different frame configurations")
print(f"💡 Look at frame_00.png in each folder to see which one looks correct")

