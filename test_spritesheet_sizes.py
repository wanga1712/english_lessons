"""
Тестирование разных размеров кадров для спрайт-листа
"""
from PIL import Image

gif_path = r'C:\Users\wangr\Downloads\6d130ef633b79c8f11dd7cd227c675ba.gif'
img = Image.open(gif_path)
width, height = img.size

print(f"Image size: {width}x{height}")
print("\nPossible frame sizes:")

# Попробуем разные размеры кадров
possible_sizes = [
    (100, height),  # 5 кадров по 100px
    (125, height),  # 4 кадра по 125px
    (71, height),   # ~7 кадров
    (83, height),   # ~6 кадров
    (width // 5, height),  # 5 кадров
    (width // 6, height),  # 6 кадров
    (width // 7, height),  # 7 кадров
]

for fw, fh in possible_sizes:
    frames_h = width // fw
    frames_v = height // fh if fh < height else 1
    total = frames_h * frames_v
    if frames_h > 0 and total > 1:
        print(f"  {fw}x{fh}: {frames_h} frames horizontally, {total} total frames")

# Самый вероятный вариант - 5 кадров по 100px
frame_width = 100
frame_height = height
frames_count = width // frame_width

print(f"\nRecommended: {frame_width}x{frame_height} ({frames_count} frames)")

