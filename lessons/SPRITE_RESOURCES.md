# Ресурсы для спрайтов Phaser

## Бесплатные ресурсы

### 1. OpenGameArt.org
**URL:** https://opengameart.org/
- ✅ Огромная коллекция бесплатных спрайтов
- ✅ Разные лицензии (CC0, CC-BY, GPL)
- ✅ Категории: персонажи, тайлы, эффекты
- ✅ Поиск по тегам: "hero", "character", "fantasy"

**Рекомендации:**
- Ищите: "fantasy hero", "adventure character", "RPG sprite"
- Формат: PNG с прозрачностью
- Размер: 32x32, 64x64, 128x128 пикселей

### 2. Itch.io
**URL:** https://itch.io/game-assets/free
- ✅ Множество бесплатных ассетов
- ✅ Можно фильтровать по лицензиям
- ✅ Разные стили (пиксель-арт, вектор, реализм)

### 3. Kenney.nl
**URL:** https://kenney.nl/assets
- ✅ Все ассеты бесплатные (CC0)
- ✅ Простой, современный стиль
- ✅ Готовые наборы для игр

### 4. Craftpix.net
**URL:** https://craftpix.net/freebies/
- ✅ Бесплатные наборы (требуется регистрация)
- ✅ Хорошее качество
- ✅ Разные стили

### 5. GameDev Market
**URL:** https://www.gamedevmarket.net/category/2d/free/
- ✅ Бесплатные и платные ассеты
- ✅ Высокое качество
- ✅ Разные стили

### 6. Lospec
**URL:** https://lospec.com/palette-list
- ✅ Палитры для пиксель-арта
- ✅ Спрайты в пиксель-стиле
- ✅ Инструменты для создания спрайтов

## Платные ресурсы (если нужно высокое качество)

- **Unity Asset Store** - можно использовать в Phaser
- **GameDev Market** - платные ассеты высокого качества
- **Craftpix.net** - платные наборы

## Для вашего проекта (Heroes 3 style)

### Что искать:
- "fantasy hero sprite"
- "adventure map character"
- "isometric hero"
- "RPG character sprite"
- "medieval hero"
- "sword hero character"

### Форматы:
- **PNG** с прозрачностью (alpha channel)
- **JSON** для спрайт-листов (atlas)
- Размеры: 32x32, 64x64, 128x128, 256x256

### Как использовать в Phaser:

#### Вариант 1: Одиночный спрайт (PNG)
```javascript
// В preload()
this.load.image('hero', 'path/to/hero.png');

// В create()
const hero = this.add.image(x, y, 'hero');
hero.setScale(2); // Увеличить размер
```

#### Вариант 2: Спрайт-лист (Sprite Sheet)
```javascript
// В preload()
this.load.spritesheet('hero', 'path/to/hero-sheet.png', {
  frameWidth: 64,
  frameHeight: 64
});

// Создать анимации
this.anims.create({
  key: 'idle',
  frames: this.anims.generateFrameNumbers('hero', { start: 0, end: 3 }),
  frameRate: 8,
  repeat: -1
});

// Использовать
const hero = this.add.sprite(x, y, 'hero');
hero.play('idle');
```

#### Вариант 3: Атлас (Texture Atlas)
```javascript
// В preload()
this.load.atlas('heroAtlas', 'path/to/hero.png', 'path/to/hero.json');

// Использовать
const hero = this.add.sprite(x, y, 'heroAtlas', 'hero-idle-1');
```

## Рекомендации для вашего проекта

1. **Стиль:** Изометрический или вид сверху (как Heroes 3)
2. **Размер:** 64x64 или 128x128 пикселей
3. **Анимации:** Idle, walk, attack (если есть)
4. **Цвета:** Яркие, контрастные (для видимости на карте)

## Примеры поиска

### OpenGameArt.org:
- Поиск: "fantasy hero" → Фильтр: Characters → Лицензия: CC0
- Поиск: "RPG character" → Фильтр: 2D → Размер: 64x64

### Itch.io:
- Поиск: "free hero sprite" → Фильтр: Free → Стиль: Pixel Art

## Лицензии

⚠️ **Важно:** Всегда проверяйте лицензию!
- **CC0** - можно использовать без ограничений
- **CC-BY** - нужно указать автора
- **GPL** - нужно открыть исходный код проекта
- **Commercial** - можно использовать в коммерческих проектах

## Где разместить спрайты в проекте

```
lessons/static/lessons/img/
  ├── characters/
  │   ├── hero-idle.png
  │   ├── hero-walk.png
  │   └── hero-attack.png
  └── tileset/
      └── map-tiles.png
```

## Быстрый старт

1. Скачайте спрайт с OpenGameArt.org
2. Положите в `lessons/static/lessons/img/characters/`
3. Используйте в коде:
```javascript
this.load.image('hero', '{% static "lessons/img/characters/hero.png" %}');
```

