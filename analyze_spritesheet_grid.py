"""
Анализ спрайт-листа для определения структуры (сетка или ряд)
"""
from PIL import Image
import os

spritesheet_path = 'lessons/static/lessons/img/characters/hero-spritesheet.png'

if not os.path.exists(spritesheet_path):
    print(f"File not found: {spritesheet_path}")
    exit(1)

img = Image.open(spritesheet_path)
width, height = img.size

print(f"Spritesheet size: {width}x{height}")
print("\nAnalyzing possible grid structures:")

# Попробуем разные размеры кадров
possible_frame_sizes = [
    (64, 64), (64, 96), (64, 128),
    (96, 64), (96, 96), (96, 128),
    (100, 100), (100, 120), (100, 150),
    (128, 64), (128, 96), (128, 128),
    (150, 150), (150, 200),
    (200, 200), (200, 250),
]

best_match = None
best_score = 0

for fw, fh in possible_frame_sizes:
    cols = width // fw
    rows = height // fh
    total_frames = cols * rows
    
    # Проверяем, насколько хорошо делится
    width_remainder = width % fw
    height_remainder = height % fh
    
    if cols > 0 and rows > 0 and total_frames > 1:
        score = total_frames - (width_remainder + height_remainder) / 10
        if score > best_score:
            best_score = score
            best_match = (fw, fh, cols, rows, total_frames)

if best_match:
    fw, fh, cols, rows, total = best_match
    print(f"\nBest match:")
    print(f"  Frame size: {fw}x{fh}")
    print(f"  Grid: {cols}x{rows} = {total} frames")
    print(f"\nPhaser code:")
    print(f"this.load.spritesheet('hero', '{{% static \"lessons/img/characters/hero-spritesheet.png\" %}}', {{")
    print(f"  frameWidth: {fw},")
    print(f"  frameHeight: {fh}")
    print(f"}});")
    print(f"\n// Total frames: {total}")
    print(f"// Grid: {cols} columns x {rows} rows")
    
    # Покажем пример разделения на кадры
    print(f"\nFrame layout:")
    for row in range(rows):
        for col in range(cols):
            frame_num = row * cols + col
            print(f"  Frame {frame_num}: column {col}, row {row}")
else:
    print("Could not determine frame structure")
    print("Trying manual inspection...")
    
    # Попробуем найти границы по цвету
    pixels = img.load()
    # Ищем вертикальные линии (возможные границы)
    vertical_lines = []
    for x in range(0, width, 10):
        # Проверяем столбец на однородность (возможная граница)
        colors = [pixels[x, y] for y in range(0, height, 10)]
        if len(set(colors)) < 3:  # Мало разных цветов = возможная граница
            vertical_lines.append(x)
    
    print(f"Possible vertical boundaries: {vertical_lines[:10]}")

