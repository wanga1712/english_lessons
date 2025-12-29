"""
Точное определение размера кадра в спрайт-листе
"""
from PIL import Image
import os

spritesheet_path = 'lessons/static/lessons/img/characters/hero-spritesheet.png'

if not os.path.exists(spritesheet_path):
    print(f"File not found: {spritesheet_path}")
    exit(1)

img = Image.open(spritesheet_path)
width, height = img.size
pixels = img.load()

print(f"Spritesheet size: {width}x{height}")
print("\nTrying to find frame boundaries by analyzing pixel differences...")

# Метод 1: Ищем вертикальные границы (где меняется контент)
def find_vertical_boundaries():
    """Ищем вертикальные линии, где меняется контент"""
    boundaries = [0]  # Начинаем с 0
    
    # Проверяем каждые 5 пикселей
    for x in range(5, width, 5):
        # Сравниваем столбцы слева и справа
        left_col = [pixels[x-5, y] for y in range(0, min(100, height), 5)]
        right_col = [pixels[x, y] for y in range(0, min(100, height), 5)]
        
        # Если разница большая, это может быть граница
        diff = sum(1 for i in range(len(left_col)) if left_col[i] != right_col[i])
        if diff > len(left_col) * 0.3:  # 30% пикселей отличаются
            boundaries.append(x)
    
    boundaries.append(width)
    
    # Находим наиболее частый интервал
    intervals = [boundaries[i+1] - boundaries[i] for i in range(len(boundaries)-1)]
    if intervals:
        most_common = max(set(intervals), key=intervals.count)
        return most_common, boundaries
    
    return None, boundaries

# Метод 2: Пробуем стандартные размеры
def test_common_sizes():
    """Тестируем стандартные размеры кадров"""
    common_sizes = [
        (100, 100), (100, 117), (100, 88),
        (125, 117), (125, 88),
        (83, 88), (83, 117),
        (71, 88), (71, 117),
        (250, 117), (250, 176),
        (166, 117), (166, 176),
    ]
    
    results = []
    for fw, fh in common_sizes:
        cols = width // fw
        rows = height // fh
        total = cols * rows
        
        w_remainder = width % fw
        h_remainder = height % fh
        
        if cols > 0 and rows > 0 and w_remainder < fw * 0.1 and h_remainder < fh * 0.1:
            score = total - (w_remainder + h_remainder) / 10
            results.append((fw, fh, cols, rows, total, score))
    
    return sorted(results, key=lambda x: x[5], reverse=True)

# Метод 3: Если это просто кадры в ряд
def test_horizontal_only():
    """Проверяем, может быть это просто кадры в один ряд"""
    # 500 / разные размеры
    widths = [100, 125, 166, 250, 500]
    results = []
    
    for fw in widths:
        if width % fw == 0:
            cols = width // fw
            fh = height  # Высота = высота всего спрайт-листа
            results.append((fw, fh, cols, 1, cols))
    
    return results

print("\n=== Method 1: Analyzing pixel boundaries ===")
frame_width, boundaries = find_vertical_boundaries()
if frame_width:
    print(f"Detected frame width: {frame_width}px")
    print(f"Boundaries: {boundaries[:10]}...")
    cols = len(boundaries) - 1
    print(f"Estimated columns: {cols}")
    print(f"Frame height: {height}px (single row)")
    print(f"\nRecommended: {frame_width}x{height} ({cols} frames in one row)")

print("\n=== Method 2: Testing common sizes ===")
results = test_common_sizes()
for fw, fh, cols, rows, total, score in results[:5]:
    print(f"  {fw}x{fh}: {cols}x{rows} grid = {total} frames (score: {score:.1f})")

print("\n=== Method 3: Single row (horizontal only) ===")
horizontal_results = test_horizontal_only()
for fw, fh, cols, rows, total in horizontal_results:
    print(f"  {fw}x{fh}: {cols} frames in one row")

# Рекомендация
print("\n=== RECOMMENDATION ===")
if frame_width and frame_width < width:
    print(f"Use: frameWidth={frame_width}, frameHeight={height}")
    print(f"This gives {width // frame_width} frames in one row")
elif horizontal_results:
    best = horizontal_results[0]
    print(f"Use: frameWidth={best[0]}, frameHeight={best[1]}")
    print(f"This gives {best[2]} frames in one row")
elif results:
    best = results[0]
    print(f"Use: frameWidth={best[0]}, frameHeight={best[1]}")
    print(f"This gives {best[4]} frames in {best[2]}x{best[3]} grid")

