/**
 * Модуль для рендеринга карточек
 * Размер: ~140 строк
 */

const CardRenderer = {
    iconMap: {
        'sun': '☀️', 'cloud': '☁️', 'rain': '🌧️', 'wind': '💨',
        'snow': '❄️', 'dog': '🐕', 'cat': '🐱', 'bird': '🐦',
        'fish': '🐟', 'run': '🏃', 'jump': '🦘', 'swim': '🏊',
        'fly': '✈️', 'dance': '💃', 'red': '🔴', 'blue': '🔵',
        'green': '🟢', 'yellow': '🟡', 'orange': '🟠', 'purple': '🟣'
    },

    cardTypeLabels: {
        'repeat': 'Повторить',
        'translate': 'Перевести',
        'choose': 'Выбрать',
        'color': 'Цвет',
        'speak': 'Проговорить',
        'match': 'Сопоставить',
        'spelling': 'Написание',
        'new_words': 'Новые слова',
        'writing': 'Письмо'
    },

    /**
     * Получение метки типа карточки
     */
    getCardTypeLabel(type) {
        return this.cardTypeLabels[type] || type;
    },

    /**
     * Генерация HTML для иконки
     */
    renderIcon(card) {
        if (card.icon_name) {
            return `<div class="card-icon">${this.iconMap[card.icon_name] || '📝'}</div>`;
        }
        if (card.image_url) {
            return `<img src="${card.image_url}" alt="Card image" class="card-image">`;
        }
        return '';
    },

    /**
     * Генерация HTML для вариантов ответа
     */
    renderOptions(card, currentCardIndex) {
        if (!card.options || card.options.length === 0) {
            return '';
        }
        
        let html = '<div class="card-options">';
        card.options.forEach((option, index) => {
            html += `<div class="option" data-option="${index}" onclick="window.LessonApp.handleOptionClick(${index}, '${option}')">${option}</div>`;
        });
        html += '</div>';
        return html;
    },

    /**
     * Генерация HTML для кнопки озвучки
     */
    renderSpeakButton(card) {
        if (card.card_type === 'repeat' || card.card_type === 'speak' || card.card_type === 'new_words') {
            return `<button class="speak-button" onclick="window.LessonApp.speakText('${card.question_text.replace(/'/g, "\\'")}')">
                <i class="fas fa-volume-up"></i> Послушать и повторить
            </button>`;
        }
        return '';
    },

    /**
     * Генерация HTML для spelling карточки
     */
    renderSpelling(card, currentCardIndex) {
        const scrambledLetters = card.extra_data?.scrambledLetters || [];
        
        if (scrambledLetters.length > 0) {
            return `
                <div style="margin-top: 20px;">
                    <div style="text-align: center; margin-bottom: 20px; font-size: 18px; font-weight: 600; color: #667eea;">
                        Собери слово из букв:
                    </div>
                    <div id="spelling-answer-${currentCardIndex}" style="
                        display: flex; justify-content: center; gap: 8px; margin-bottom: 20px;
                        min-height: 60px; padding: 15px; background: #f8f9fa;
                        border-radius: 12px; border: 2px dashed #e9ecef;
                    "></div>
                    <div id="spelling-letters-${currentCardIndex}" style="
                        display: flex; justify-content: center; flex-wrap: wrap;
                        gap: 10px; margin-bottom: 20px;
                    ">
                        ${scrambledLetters.map((letter, idx) => `
                            <div class="spelling-letter" data-letter="${letter}" data-index="${idx}"
                                 style="width: 50px; height: 50px;
                                 background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                 color: white; font-size: 24px; font-weight: bold;
                                 display: flex; align-items: center; justify-content: center;
                                 border-radius: 12px; cursor: pointer; user-select: none;
                                 transition: all 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"
                                 onclick="addLetterToSpelling(${currentCardIndex}, '${letter}', ${idx})"
                                 onmouseover="this.style.transform='scale(1.1)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.2)'"
                                 onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.1)'">
                                ${letter.toUpperCase()}
                            </div>
                        `).join('')}
                    </div>
                    <div style="display: flex; gap: 10px; justify-content: center;">
                        <button class="speak-button" onclick="checkSpelling(${currentCardIndex}, '${card.correct_answer}')" style="margin: 0;">
                            Проверить
                        </button>
                        <button class="speak-button" onclick="clearSpelling(${currentCardIndex})" style="margin: 0; background: #6c757d;">
                            Очистить
                        </button>
                    </div>
                </div>
            `;
        }
        
        if (card.options && card.options.length > 0) {
            return this.renderOptions(card, currentCardIndex);
        }
        
        return `
            <div style="margin-top: 20px;">
                <input type="text" id="spelling-input-${currentCardIndex}" placeholder="Напиши слово..." 
                       style="width: 100%; padding: 12px; font-size: 18px; border: 2px solid #e9ecef; border-radius: 8px; text-align: center;"
                       onkeypress="if(event.key==='Enter') window.LessonApp.handleSpellingSubmit(${currentCardIndex}, '${card.correct_answer}')">
                <button class="speak-button" onclick="window.LessonApp.handleSpellingSubmit(${currentCardIndex}, '${card.correct_answer}')" style="margin-top: 12px;">
                    Проверить
                </button>
            </div>
        `;
    },

    /**
     * Генерация HTML для writing карточки
     */
    renderWriting(card, currentCardIndex) {
        if (card.options && card.options.length > 0) {
            return this.renderOptions(card, currentCardIndex);
        }
        
        return `
            <div style="margin-top: 20px;">
                <input type="text" id="spelling-input-${currentCardIndex}" placeholder="Напиши слово..." 
                       style="width: 100%; padding: 12px; font-size: 18px; border: 2px solid #e9ecef; border-radius: 8px; text-align: center;"
                       onkeypress="if(event.key==='Enter') window.LessonApp.handleSpellingSubmit(${currentCardIndex}, '${card.correct_answer}')">
                <button class="speak-button" onclick="window.LessonApp.handleSpellingSubmit(${currentCardIndex}, '${card.correct_answer}')" style="margin-top: 12px;">
                    Проверить
                </button>
            </div>
        `;
    },

    /**
     * Рендеринг полной карточки
     */
    renderCard(card, currentCardIndex, totalCards) {
        const iconHtml = this.renderIcon(card);
        const speakButtonHtml = this.renderSpeakButton(card);
        
        let contentHtml = '';
        if (card.card_type === 'spelling') {
            contentHtml = this.renderSpelling(card, currentCardIndex);
        } else if (card.card_type === 'writing') {
            contentHtml = this.renderWriting(card, currentCardIndex);
        } else {
            contentHtml = this.renderOptions(card, currentCardIndex);
        }
        
        const additionalBadge = (card.extra_data && card.extra_data.isAdditional) 
            ? '<span style="background: #fbbf24; color: white; padding: 4px 8px; border-radius: 8px; font-size: 11px; margin-left: 8px;">✨ Новое</span>'
            : '';
        
        return `
            <div class="card active" id="card-${currentCardIndex}">
                <div class="card-header">
                    <span class="card-type">${this.getCardTypeLabel(card.card_type)}${additionalBadge}</span>
                    <span class="card-number">Карточка ${currentCardIndex + 1} из ${totalCards}</span>
                </div>
                ${iconHtml}
                <div class="card-question">${card.question_text}</div>
                <div class="card-prompt">${card.prompt_text}</div>
                ${speakButtonHtml}
                ${contentHtml}
                <div id="hint-box-${currentCardIndex}" class="hint-box hidden"></div>
                <div id="translation-box-${currentCardIndex}" class="translation-box hidden"></div>
            </div>
        `;
    }
};

