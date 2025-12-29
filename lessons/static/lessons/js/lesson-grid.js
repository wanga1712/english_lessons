/**
 * JavaScript для сетки карточек по темам
 */

// Глобальные переменные
let currentAttemptId = null;
let cardStatuses = {};
// Утилита очистки текста от экранированных символов
const cleanText = (text) => {
  if (!text) return '';
  let cleaned = String(text);
  cleaned = cleaned.replace(/\\\\'/g, "'");
  cleaned = cleaned.replace(/\\\\"/g, '"');
  cleaned = cleaned.replace(/\\'/g, "'");
  cleaned = cleaned.replace(/\\"/g, '"');
  cleaned = cleaned.replace(/&#39;/g, "'");
  cleaned = cleaned.replace(/&apos;/g, "'");
  cleaned = cleaned.replace(/&quot;/g, '"');
  return cleaned.trim();
};

// Инициализация
document.addEventListener('DOMContentLoaded', async () => {
    // #region agent log
    fetch('http://127.0.0.1:7244/ingest/47fa6f77-db98-4c70-bd7a-f564ec61d812',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'lesson-grid.js:23',message:'DOMContentLoaded fired',data:{hasCardsData:!!cardsData,hasTopicsData:!!topicsData,cardsDataLength:cardsData?.length,topicsDataKeys:topicsData?Object.keys(topicsData):[]},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    await initLesson();
    // renderTopicsGrid вызывается внутри initLesson после загрузки статусов
    updateAvatar();
});

// Инициализация урока
async function initLesson() {
    // #region agent log
    fetch('http://127.0.0.1:7244/ingest/47fa6f77-db98-4c70-bd7a-f564ec61d812',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'lesson-grid.js:30',message:'initLesson called',data:{lessonId,hasCardsData:!!cardsData,hasTopicsData:!!topicsData,cardsDataType:typeof cardsData,topicsDataType:typeof topicsData},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    try {
        // Сначала загружаем статусы из переданных данных карточек
        if (cardsData && Array.isArray(cardsData)) {
            cardsData.forEach(card => {
                if (card.id && card.card_status !== undefined) {
                    cardStatuses[card.id] = {
                        status: card.card_status || 0,
                        color: card.status_color || getStatusColor(card.card_status || 0),
                        attempts_count: card.attempts_count || 0
                    };
                }
            });
            console.log('Initial card statuses from cardsData:', cardStatuses);
        }
        
        // Загружаем прогресс пользователя
        const progressResponse = await fetch('/api/progress/');
        if (progressResponse.ok) {
            const progress = await progressResponse.json();
            document.getElementById('experience').textContent = progress.total_experience || 0;
            document.getElementById('level').textContent = progress.current_level || 1;
        }
        
        // Начинаем попытку урока
        const attemptResponse = await fetch(`/api/lessons/${lessonId}/start/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (attemptResponse.ok) {
            const data = await attemptResponse.json();
            currentAttemptId = data.attempt_id;
        }
        
        // Загружаем актуальные статусы карточек (обновляем существующие)
        await loadCardStatuses();
        
        // Рендерим карточки после загрузки всех данных
        // #region agent log
        fetch('http://127.0.0.1:7244/ingest/47fa6f77-db98-4c70-bd7a-f564ec61d812',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'lesson-grid.js:69',message:'About to call renderTopicsGrid',data:{hasTopicsData:!!topicsData,topicsDataKeys:topicsData?Object.keys(topicsData):[],topicsDataValue:topicsData},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
        // #endregion
        renderTopicsGrid();
    } catch (error) {
        // #region agent log
        fetch('http://127.0.0.1:7244/ingest/47fa6f77-db98-4c70-bd7a-f564ec61d812',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'lesson-grid.js:71',message:'initLesson error',data:{errorMessage:error.message,errorStack:error.stack},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
        // #endregion
        console.error('Ошибка инициализации:', error);
    }
}

// Загрузка статусов карточек
async function loadCardStatuses() {
    try {
        console.log('Loading card statuses for lesson:', lessonId);
        const response = await fetch(`/api/lessons/${lessonId}/card_statuses/`);
        console.log('Status response:', response.status, response.ok);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Status data received:', data);
            const loadedStatuses = data.card_statuses || {};
            
            // Очищаем старые статусы
            cardStatuses = {};
            
            // Преобразуем формат данных, если нужно
            for (const [cardId, statusData] of Object.entries(loadedStatuses)) {
                const cardIdNum = parseInt(cardId);
                if (statusData && typeof statusData === 'object') {
                    cardStatuses[cardIdNum] = {
                        status: statusData.status || statusData,
                        color: statusData.color || getStatusColor(statusData.status || statusData),
                        attempts_count: statusData.attempts_count || 0
                    };
                } else {
                    // Если пришел просто статус (число)
                    cardStatuses[cardIdNum] = {
                        status: statusData,
                        color: getStatusColor(statusData),
                        attempts_count: 0
                    };
                }
            }
            
            console.log('Loaded card statuses:', cardStatuses);
            console.log('Total statuses loaded:', Object.keys(cardStatuses).length);
            
            // Перерисовываем карточки после загрузки статусов
            renderTopicsGrid();
        } else {
            console.error('Failed to load statuses:', response.status, response.statusText);
            const errorData = await response.json().catch(() => ({}));
            console.error('Error data:', errorData);
        }
    } catch (error) {
        console.error('Ошибка загрузки статусов:', error);
    }
}

// Обновление аватара
function updateAvatar() {
    if (avatarData) {
        document.getElementById('avatar-emoji').textContent = avatarData.emoji || '🎓';
        document.getElementById('avatar-name').textContent = avatarData.name || 'Ученик';
        document.getElementById('avatar-score').textContent = avatarData.score?.toFixed(1) || '0.0';
    }
}

// Рендеринг сетки тем
function renderTopicsGrid() {
    // #region agent log
    fetch('http://127.0.0.1:7244/ingest/47fa6f77-db98-4c70-bd7a-f564ec61d812',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'lesson-grid.js:134',message:'renderTopicsGrid called',data:{hasTopicsData:!!topicsData,topicsDataType:typeof topicsData,topicsDataKeys:topicsData?Object.keys(topicsData):[]},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
    // #endregion
    const container = document.getElementById('topics-grid');
    // #region agent log
    fetch('http://127.0.0.1:7244/ingest/47fa6f77-db98-4c70-bd7a-f564ec61d812',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'lesson-grid.js:136',message:'Container check',data:{containerFound:!!container,containerId:container?.id},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'F'})}).catch(()=>{});
    // #endregion
    if (!container) return;
    
    container.innerHTML = '';
    
    // Сортируем темы
    const sortedTopics = Object.keys(topicsData).sort();
    // #region agent log
    fetch('http://127.0.0.1:7244/ingest/47fa6f77-db98-4c70-bd7a-f564ec61d812',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'lesson-grid.js:141',message:'Topics sorted',data:{sortedTopicsCount:sortedTopics.length,sortedTopics},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'G'})}).catch(()=>{});
    // #endregion
    
    sortedTopics.forEach(topic => {
        const topicData = topicsData[topic];
        // #region agent log
        fetch('http://127.0.0.1:7244/ingest/47fa6f77-db98-4c70-bd7a-f564ec61d812',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'lesson-grid.js:143',message:'Processing topic',data:{topic,hasTopicData:!!topicData,cardsCount:topicData?.cards?.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'H'})}).catch(()=>{});
        // #endregion
        const topicSection = createTopicSection(topic, topicData);
        container.appendChild(topicSection);
    });
    // #region agent log
    fetch('http://127.0.0.1:7244/ingest/47fa6f77-db98-4c70-bd7a-f564ec61d812',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'lesson-grid.js:148',message:'renderTopicsGrid completed',data:{containerChildrenCount:container.children.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'I'})}).catch(()=>{});
    // #endregion
}

// Создание секции темы
function createTopicSection(topic, topicData) {
    const section = document.createElement('div');
    section.className = 'topic-section';
    
    const cards = topicData.cards || [];
    const completedCount = cards.filter(card => {
        const status = cardStatuses[card.id]?.status || card.card_status || 0;
        return status > 0;
    }).length;
    
    const totalScore = cards.reduce((sum, card) => {
        const status = cardStatuses[card.id]?.status || card.card_status || 0;
        return sum + status;
    }, 0);
    
    const avgScore = completedCount > 0 ? (totalScore / completedCount).toFixed(1) : '0.0';
    
    section.innerHTML = `
        <div class="topic-header">
            <div class="topic-title">
                <span>${getTopicEmoji(topic)}</span>
                <span>${topicData.name || topic}</span>
            </div>
            <div class="topic-stats">
                ${completedCount} / ${cards.length} карточек • Средний балл: ${avgScore}
            </div>
        </div>
        <div class="cards-grid">
            ${cards.map(card => createCardHTML(card)).join('')}
        </div>
    `;
    
            // Добавляем обработчики кликов на карточки
            section.querySelectorAll('.card-item').forEach((cardEl, index) => {
                cardEl.addEventListener('click', () => {
                    const card = cards[index];
                    // Открываем упражнение в новом окне
                    const exerciseUrl = `/lesson/${lessonId}/card/${card.id}/`;
                    window.open(exerciseUrl, '_blank', 'width=800,height=600,scrollbars=yes');
                });
            });
    
    return section;
}

// Создание HTML карточки
function createCardHTML(card) {
    // Используем статус из cardStatuses, если есть, иначе из card.card_status, иначе 0
    const statusInfo = cardStatuses[card.id];
    const status = statusInfo?.status ?? card.card_status ?? 0;
    const statusColor = statusInfo?.color || getStatusColor(status);
    const statusBadge = getStatusBadge(status);
  const questionText = cleanText(card.question_text || card.prompt_text || card.correct_answer || '');
  const promptText = cleanText(card.prompt_text || '');
    
    return `
        <div class="card-item status-${statusColor}" data-card-id="${card.id}">
            ${statusBadge}
            <div class="card-content">
                ${card.icon_name ? `<div class="card-icon">${getIconEmoji(card.icon_name)}</div>` : ''}
        <div class="card-question">${questionText}</div>
        <div class="card-prompt">${promptText}</div>
                <div class="card-type">${getCardTypeLabel(card.card_type)}</div>
            </div>
        </div>
    `;
}

// Получение цвета статуса
function getStatusColor(status) {
    if (status === 0) return 'gray';
    if (status === 3) return 'yellow';
    if (status === 5) return 'green';
    return 'gray';
}

// Получение бейджа статуса
function getStatusBadge(status) {
    if (status === 0) return '<div class="card-status-badge red">✗</div>';
    if (status === 3) return '<div class="card-status-badge yellow">!</div>';
    if (status === 5) return '<div class="card-status-badge green">✓</div>';
    return '';
}

// Получение эмодзи темы
function getTopicEmoji(topic) {
    const emojis = {
        'weather': '🌤️',
        'actions': '🏃',
        'colors': '🎨',
        'animals': '🐾',
        'food': '🍎',
        'family': '👨‍👩‍👧',
        'body': '👤',
        'numbers': '🔢',
        'general': '📚',
        'review': '🔄'
    };
    return emojis[topic] || '📝';
}

// Получение эмодзи иконки
function getIconEmoji(iconName) {
    const iconMap = {
        'sun': '☀️', 'cloud': '☁️', 'rain': '🌧️', 'wind': '💨',
        'snow': '❄️', 'dog': '🐕', 'cat': '🐱', 'bird': '🐦',
        'fish': '🐟', 'run': '🏃', 'jump': '🦘', 'swim': '🏊',
        'fly': '✈️', 'dance': '💃', 'red': '🔴', 'blue': '🔵',
        'green': '🟢', 'yellow': '🟡', 'orange': '🟠', 'purple': '🟣'
    };
    return iconMap[iconName] || '📝';
}

// Получение названия типа карточки
function getCardTypeLabel(type) {
    const labels = {
        'repeat': 'Повторить',
        'translate': 'Перевести',
        'choose': 'Выбрать',
        'color': 'Цвет',
        'speak': 'Проговорить',
        'match': 'Сопоставить',
        'spelling': 'Написание',
        'new_words': 'Новые слова',
        'writing': 'Письмо'
    };
    return labels[type] || type;
}

// Обновление статуса карточки после выполнения
window.addEventListener('message', function(event) {
    if (event.data.type === 'card_completed') {
        const cardId = event.data.card_id;
        const status = event.data.status;
        const color = event.data.color;
        
        // Обновляем статус в cardStatuses
        cardStatuses[cardId] = {
            status: status,
            color: color,
            attempts_count: cardStatuses[cardId]?.attempts_count || 0
        };
        
        // Обновляем отображение карточки
        const cardEl = document.querySelector(`[data-card-id="${cardId}"]`);
        if (cardEl) {
            cardEl.className = `card-item status-${color}`;
            const badge = cardEl.querySelector('.card-status-badge');
            if (badge) {
                badge.className = `card-status-badge ${color}`;
                if (status === 0) badge.textContent = '✗';
                else if (status === 3) badge.textContent = '!';
                else if (status === 5) badge.textContent = '✓';
            }
        }
        
        // Обновляем аватар
        updateAvatar();
    }
});

