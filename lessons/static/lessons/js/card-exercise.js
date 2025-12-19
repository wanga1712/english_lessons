/**
 * JavaScript для выполнения одной карточки
 */

let currentAttemptId = attemptId;
let cardCompleted = false;

// Инициализация
document.addEventListener('DOMContentLoaded', async () => {
    await initCardExercise();
    renderCard();
});

// Инициализация упражнения
async function initCardExercise() {
    try {
        // Если нет attempt_id, создаём попытку
        if (!currentAttemptId) {
            const response = await fetch(`/api/lessons/${lessonId}/start/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (response.ok) {
                const data = await response.json();
                currentAttemptId = data.attempt_id;
            }
        }
    } catch (error) {
        console.error('Ошибка инициализации:', error);
    }
}

// Рендеринг карточки
function renderCard() {
    const container = document.getElementById('card-exercise-container');
    if (!container) {
        console.error('Container not found!');
        return;
    }
    
    if (!cardData) {
        console.error('cardData is not defined!');
        container.innerHTML = '<div style="color: red; padding: 20px;">Ошибка: данные карточки не загружены</div>';
        return;
    }
    
    const card = cardData;
    console.log('Rendering card:', card);
    console.log('Card type:', card.card_type);
    console.log('Question text:', card.question_text);
    console.log('Extra data:', card.extra_data);
    
    const iconHtml = card.icon_name ? `<div class="card-icon">${getIconEmoji(card.icon_name)}</div>` : '';
    
    let contentHtml = '';
    try {
        if (card.card_type === 'spelling') {
            contentHtml = renderSpelling(card);
            console.log('renderSpelling returned:', contentHtml ? 'HTML' : 'EMPTY');
        } else if (card.card_type === 'writing') {
            contentHtml = renderWriting(card);
            console.log('renderWriting returned:', contentHtml ? 'HTML' : 'EMPTY');
        } else if (card.card_type === 'repeat' || card.card_type === 'speak' || card.card_type === 'new_words') {
            contentHtml = renderSpeak(card);
            console.log('renderSpeak returned:', contentHtml ? 'HTML' : 'EMPTY');
        } else {
            contentHtml = renderOptions(card);
            console.log('renderOptions returned:', contentHtml ? 'HTML' : 'EMPTY');
        }
    } catch (e) {
        console.error('Error rendering card:', e);
        contentHtml = `<div style="color: red; padding: 20px;">Ошибка: ${e.message}</div>`;
    }
    
    // Убираем экранированные кавычки из текста
    const cleanText = (text) => {
        if (!text) return '';
        let cleaned = String(text);
        // Убираем экранированные кавычки (могут быть разные варианты)
        cleaned = cleaned.replace(/\\'/g, "'");
        cleaned = cleaned.replace(/\\"/g, '"');
        cleaned = cleaned.replace(/&#39;/g, "'");
        cleaned = cleaned.replace(/&quot;/g, '"');
        cleaned = cleaned.replace(/&apos;/g, "'");
        // Убираем двойное экранирование
        cleaned = cleaned.replace(/\\\\'/g, "'");
        cleaned = cleaned.replace(/\\\\"/g, '"');
        return cleaned.trim();
    };
    
    const questionText = cleanText(card.question_text);
    const promptText = cleanText(card.prompt_text);
    
    console.log('Original question_text:', card.question_text);
    console.log('Cleaned question_text:', questionText);
    
    console.log('Final contentHtml length:', contentHtml ? contentHtml.length : 0);
    
    if (!contentHtml || contentHtml.trim() === '') {
        console.error('contentHtml is EMPTY!');
        contentHtml = `<div style="padding: 20px; text-align: center; color: #6b7280; border: 2px solid red;">
            <p style="color: red; font-weight: bold;">ОШИБКА: Контент карточки пустой!</p>
            <p>Тип: ${card.card_type || 'неизвестен'}</p>
            <p>Question: ${questionText || 'нет'}</p>
            <p>Extra data: ${JSON.stringify(card.extra_data || {})}</p>
        </div>`;
    }
    
    container.innerHTML = `
        <div class="card-exercise">
            <div class="card-header">
                <span class="card-type">${getCardTypeLabel(card.card_type || 'unknown')}</span>
            </div>
            ${iconHtml}
            ${questionText ? `<div class="card-question">${questionText}</div>` : ''}
            ${promptText ? `<div class="card-prompt">${promptText}</div>` : ''}
            ${contentHtml}
            <div id="hint-box" class="hint-box hidden"></div>
            <div id="translation-box" class="translation-box hidden"></div>
            <div id="result-message" class="result-message hidden"></div>
        </div>
    `;
}

// Рендеринг вариантов ответа
function renderOptions(card) {
    if (!card) {
        console.error('renderOptions: card is null');
        return '<div style="color: red;">Ошибка: нет данных карточки</div>';
    }
    
    if (!card.options || card.options.length === 0) {
        console.warn('renderOptions: no options for card', card);
        return '<div style="padding: 20px; text-align: center; color: #6b7280;">Нет вариантов ответа</div>';
    }
    
    let html = '<div class="card-options">';
    card.options.forEach((option, index) => {
        const safeOption = String(option || '').replace(/'/g, "\\'");
        html += `<div class="option" onclick="handleOptionClick('${safeOption}')">${option}</div>`;
    });
    html += '</div>';
    return html;
}

// Рендеринг spelling
function renderSpelling(card) {
    if (!card) {
        console.error('renderSpelling: card is null');
        return '<div style="color: red;">Ошибка: нет данных карточки</div>';
    }
    
    const extraData = card.extra_data || {};
    let scrambledLetters = extraData.scrambledLetters || [];
    
    if (scrambledLetters.length === 0 && card.correct_answer) {
        const correctAnswer = String(card.correct_answer).toLowerCase().trim();
        scrambledLetters = correctAnswer.split('').filter(c => /[a-z]/.test(c));
        for (let i = scrambledLetters.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [scrambledLetters[i], scrambledLetters[j]] = [scrambledLetters[j], scrambledLetters[i]];
        }
    }
    
    if (scrambledLetters.length > 0) {
        const lettersHtml = scrambledLetters.map((letter, idx) => {
            const safeLetter = String(letter).replace(/'/g, "\\'");
            return `<div class="spelling-letter" data-letter="${safeLetter}" data-index="${idx}"
                     onclick="addLetterToSpellingCard('${safeLetter}', ${idx})"
                     style="width: 50px; height: 50px; background: #667eea; color: white; font-size: 24px; font-weight: bold; display: flex; align-items: center; justify-content: center; border-radius: 12px; cursor: pointer; transition: all 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        ${String(letter).toUpperCase()}
                    </div>`;
        }).join('');
        
        return `
            <div class="spelling-container">
                <div class="spelling-instruction">Собери слово из букв (нажимай на буквы по порядку):</div>
                <div id="spelling-answer" class="spelling-answer" style="min-height: 60px; display: flex; flex-wrap: wrap; gap: 8px; padding: 12px; border: 2px dashed #d1d5db; border-radius: 12px; margin-bottom: 16px;"></div>
                <div id="spelling-letters" class="spelling-letters" style="display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;">
                    ${lettersHtml}
                </div>
                <div class="spelling-buttons" style="margin-top: 20px; display: flex; gap: 12px; justify-content: center;">
                    <button class="btn-check" onclick="checkSpellingCard()">Проверить</button>
                    <button class="btn-clear" onclick="clearSpellingCard()" style="background: #6b7280;">Очистить</button>
                </div>
            </div>
        `;
    }
    
    return `
        <div class="input-container">
            <input type="text" id="spelling-input" placeholder="Напиши слово..." 
                   onkeypress="if(event.key==='Enter') handleTextSubmit()">
            <button class="btn-check" onclick="handleTextSubmit()">Проверить</button>
        </div>
    `;
}

// Глобальные функции для spelling карточки
let spellingAnswer = [];
let spellingLetters = [];

function addLetterToSpellingCard(letter, index) {
    const letterDiv = document.querySelector(`#spelling-letters .spelling-letter[data-index="${index}"]`);
    if (letterDiv && !letterDiv.classList.contains('used')) {
        spellingAnswer.push({letter, index});
        letterDiv.classList.add('used');
        letterDiv.style.opacity = '0.5';
        letterDiv.style.cursor = 'not-allowed';
        letterDiv.onclick = null;
        
        const answerDiv = document.getElementById('spelling-answer');
        if (answerDiv) {
            const letterSpan = document.createElement('span');
            letterSpan.className = 'spelling-answer-letter';
            letterSpan.textContent = letter.toUpperCase();
            letterSpan.style.cssText = `
                width: 50px; height: 50px; background: #22c55e; color: white;
                font-size: 24px; font-weight: bold; display: flex;
                align-items: center; justify-content: center; border-radius: 12px;
                cursor: pointer; transition: all 0.2s;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            `;
            letterSpan.onclick = () => removeLetterFromSpellingCard(index);
            answerDiv.appendChild(letterSpan);
        }
    }
}

function removeLetterFromSpellingCard(index) {
    const idx = spellingAnswer.findIndex(item => item.index === index);
    if (idx > -1) {
        spellingAnswer.splice(idx, 1);
        
        const answerDiv = document.getElementById('spelling-answer');
        const letterDiv = document.querySelector(`#spelling-letters .spelling-letter[data-index="${index}"]`);
        
        if (answerDiv && letterDiv) {
            const answerLetters = answerDiv.querySelectorAll('.spelling-answer-letter');
            if (answerLetters[idx]) {
                answerLetters[idx].remove();
            }
            
            letterDiv.classList.remove('used');
            letterDiv.style.opacity = '1';
            letterDiv.style.cursor = 'pointer';
            const letter = letterDiv.getAttribute('data-letter');
            letterDiv.onclick = () => addLetterToSpellingCard(letter, index);
        }
    }
}

function clearSpellingCard() {
    spellingAnswer = [];
    const answerDiv = document.getElementById('spelling-answer');
    if (answerDiv) {
        answerDiv.innerHTML = '';
    }
    
    const letterDivs = document.querySelectorAll('#spelling-letters .spelling-letter');
    letterDivs.forEach(div => {
        div.classList.remove('used');
        div.style.opacity = '1';
        div.style.cursor = 'pointer';
        const letter = div.getAttribute('data-letter');
        const index = parseInt(div.getAttribute('data-index'));
        div.onclick = () => addLetterToSpellingCard(letter, index);
    });
}

async function checkSpellingCard() {
    if (cardCompleted) return;
    
    const userAnswer = spellingAnswer.map(item => item.letter).join('').toLowerCase();
    if (!userAnswer) {
        alert('Собери слово из букв!');
        return;
    }
    
    await submitAnswer(userAnswer, false);
}

// Рендеринг writing
function renderWriting(card) {
    return `
        <div class="input-container">
            <input type="text" id="writing-input" placeholder="Напиши слово..." 
                   onkeypress="if(event.key==='Enter') handleTextSubmit()">
            <button class="btn-check" onclick="handleTextSubmit()">Проверить</button>
        </div>
    `;
}

// Рендеринг speak/repeat
function renderSpeak(card) {
    if (!card) return '<div>Ошибка: нет данных карточки</div>';
    
    const extraData = card.extra_data || {};
    let textToSpeak = (card.question_text || card.prompt_text || card.correct_answer || '').trim();
    let wordsToShow = [];
    
    // Проверяем extraData.words
    if (extraData.words && Array.isArray(extraData.words)) {
        wordsToShow = extraData.words.filter(w => w && String(w).trim());
        if (wordsToShow.length > 0) {
            textToSpeak = wordsToShow.join(', ');
        }
    }
    
    // Если words нет, используем question_text, prompt_text или correct_answer
    if (wordsToShow.length === 0) {
        if (textToSpeak) {
            const parts = textToSpeak.split(',').map(p => p.trim()).filter(p => p);
            wordsToShow = parts.length > 1 ? parts : [textToSpeak];
        } else {
            // Если вообще ничего нет
            return `
                <div class="speak-container">
                    <div style="padding: 20px; text-align: center; color: #6b7280;">
                        <p>Повтори фразу вслух</p>
                    </div>
                    <button class="btn-check" onclick="submitAnswer('', true)" style="width: 100%; margin-top: 12px;">
                        <i class="fas fa-check"></i> Продолжить
                    </button>
                </div>
            `;
        }
    }
    
    const recognitionText = wordsToShow[0] || textToSpeak || '';
    const safeTextToSpeak = String(textToSpeak || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
    const safeRecognitionText = String(recognitionText || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
    
    const wordsHtml = wordsToShow.map(word => {
        const safeWord = String(word || '').replace(/"/g, '&quot;').replace(/'/g, "\\'");
        return `<div style="font-size: 16px; color: #374151; margin: 8px 0; padding: 8px; background: white; border-radius: 8px;">${safeWord}</div>`;
    }).join('');
    
    return `
        <div class="speak-container">
            <div style="margin-bottom: 16px; padding: 16px; background: #f8f9fa; border-radius: 12px; text-align: center;">
                <div style="font-size: 18px; font-weight: 600; color: #1f2937; margin-bottom: 8px;">Повтори эти фразы:</div>
                ${wordsHtml}
            </div>
            <button class="btn-speak" onclick="speakText('${safeTextToSpeak}')">
                <i class="fas fa-volume-up"></i> Послушать правильное произношение
            </button>
            <div class="speak-note" style="margin-top: 16px; margin-bottom: 16px;">
                Нажми кнопку ниже и повтори фразу вслух
            </div>
            <button class="btn-check" onclick="startSpeechRecognition('${safeRecognitionText}')" style="width: 100%; margin-top: 12px;">
                <i class="fas fa-microphone"></i> Начать запись
            </button>
            <div id="recognition-status" style="margin-top: 12px; text-align: center; font-size: 14px; color: #6b7280; min-height: 20px;"></div>
            <div id="recognition-result" style="margin-top: 12px; padding: 12px; background: #f8f9fa; border-radius: 8px; text-align: center; font-size: 16px; font-weight: 600; min-height: 40px; display: none;"></div>
        </div>
    `;
}

// Обработка клика по варианту
async function handleOptionClick(userAnswer) {
    if (cardCompleted) return;
    
    await submitAnswer(userAnswer, false);
}

// Обработка текстового ввода
async function handleTextSubmit() {
    if (cardCompleted) return;
    
    const input = document.getElementById('spelling-input') || document.getElementById('writing-input');
    if (!input) return;
    
    const userAnswer = input.value.trim().toLowerCase();
    if (!userAnswer) return;
    
    await submitAnswer(userAnswer, false);
}

// Проверка spelling
async function checkSpelling() {
    if (cardCompleted) return;
    
    const answerDiv = document.getElementById('spelling-answer');
    if (!answerDiv) return;
    
    const userAnswer = Array.from(answerDiv.querySelectorAll('.spelling-answer-letter'))
        .map(el => el.textContent.toLowerCase())
        .join('');
    
    if (!userAnswer) {
        alert('Собери слово из букв!');
        return;
    }
    
    await submitAnswer(userAnswer, false);
}

// Отправка ответа
async function submitAnswer(userAnswer, isCorrectPrechecked = false) {
    if (cardCompleted) return;
    
    const card = cardData;
    let isCorrect = isCorrectPrechecked;
    
    if (!isCorrectPrechecked) {
        const extraData = card.extra_data || {};
        if (card.card_type === 'repeat' && extraData.words && Array.isArray(extraData.words)) {
            const userAnswerLower = userAnswer.toLowerCase().trim();
            const words = extraData.words.map(w => String(w || '').toLowerCase().trim()).filter(w => w);
            isCorrect = words.some(word => checkSpeechMatch(userAnswerLower, word));
        } else if (card.correct_answer) {
            isCorrect = userAnswer === card.correct_answer || 
                       userAnswer.toLowerCase() === String(card.correct_answer).toLowerCase();
        } else {
            isCorrect = true;
        }
    }
    
    // Отключаем интерфейс
    const options = document.querySelectorAll('.option');
    options.forEach(el => el.classList.add('disabled'));
    
    const input = document.getElementById('spelling-input') || document.getElementById('writing-input');
    if (input) {
        input.disabled = true;
    }
    
    const letterDivs = document.querySelectorAll('.spelling-letter');
    letterDivs.forEach(div => {
        div.style.cursor = 'not-allowed';
        div.style.opacity = '0.6';
        div.onclick = null;
    });
    
    // Подсвечиваем ответ
    if (options.length > 0 && !isCorrectPrechecked) {
        const clickedOption = Array.from(options).find(el => 
            el.textContent.trim() === userAnswer || 
            el.textContent.trim().toLowerCase() === userAnswer.toLowerCase()
        );
        if (clickedOption) {
            clickedOption.classList.add(isCorrect ? 'correct' : 'incorrect');
        }
    }
    
    try {
        const response = await fetch('/api/cards/answer/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                attempt_id: currentAttemptId,
                card_id: card.id,
                answer: userAnswer,
                is_correct: isCorrect
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            cardCompleted = true;
            showResult(data, isCorrect, card);
            
            const statusDivSubmit = document.getElementById('recognition-status');
            if (statusDivSubmit && (card.card_type === 'repeat' || card.card_type === 'speak')) {
                if (isCorrect) {
                    statusDivSubmit.innerHTML = '<span style="color: #22c55e; font-weight: 600;">✓ Правильно! Молодец!</span>';
                } else {
                    statusDivSubmit.innerHTML = '<span style="color: #ef4444; font-weight: 600;">✗ Неправильно. Попробуй еще раз!</span>';
                }
            }
            
            if (window.opener) {
                window.opener.postMessage({
                    type: 'card_completed',
                    card_id: card.id,
                    status: data.card_status,
                    color: data.status_color
                }, '*');
            }
        } else {
            alert('Ошибка отправки ответа');
        }
    } catch (error) {
        console.error('Ошибка отправки ответа:', error);
        alert('Ошибка отправки ответа. Попробуйте еще раз.');
    }
}

// Показ результата
function showResult(data, isCorrect, card) {
    console.log('showResult called:', {isCorrect, data, card});
    
    const resultDiv = document.getElementById('result-message');
    if (!resultDiv) {
        console.error('result-message element not found!');
        // Создаём элемент, если его нет
        const container = document.querySelector('.card-exercise') || document.getElementById('card-exercise-container');
        if (container) {
            const newResultDiv = document.createElement('div');
            newResultDiv.id = 'result-message';
            newResultDiv.className = 'result-message';
            container.appendChild(newResultDiv);
            return showResult(data, isCorrect, card); // Рекурсивно вызываем снова
        }
        return;
    }
    
    resultDiv.classList.remove('hidden');
    resultDiv.style.display = 'block';
    resultDiv.style.marginTop = '20px';
    resultDiv.style.padding = '20px';
    resultDiv.style.borderRadius = '12px';
    resultDiv.style.fontSize = '16px';
    
    if (isCorrect) {
        resultDiv.className = 'result-message success';
        resultDiv.style.background = '#f0fdf4';
        resultDiv.style.border = '2px solid #22c55e';
        resultDiv.style.color = '#166534';
        resultDiv.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="font-size: 32px;">✓</div>
                <div>
                    <h3 style="margin: 0 0 8px 0; font-size: 20px;">Отлично! Молодец! 🎉</h3>
                    <p style="margin: 0;">Ты правильно ответил!</p>
                    ${data.experience_gained ? `<p style="margin: 8px 0 0 0; font-weight: 600;">+${data.experience_gained} XP</p>` : ''}
                    ${card.translation_text ? `<p style="margin: 8px 0 0 0; font-style: italic;">Перевод: ${card.translation_text}</p>` : ''}
                    ${data.card_status === 5 ? '<p style="margin: 8px 0 0 0; font-weight: 600;">Идеально выполнено! 🎉</p>' : ''}
                </div>
            </div>
        `;
        
        // Показываем перевод
        if (card.translation_text) {
            const translationBox = document.getElementById('translation-box');
            if (translationBox) {
                translationBox.innerHTML = `<strong>Перевод:</strong> ${card.translation_text}`;
                translationBox.classList.remove('hidden');
                translationBox.style.display = 'block';
            }
        }
    } else {
        resultDiv.className = 'result-message error';
        resultDiv.style.background = '#fef2f2';
        resultDiv.style.border = '2px solid #ef4444';
        resultDiv.style.color = '#991b1b';
        resultDiv.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="font-size: 32px;">✗</div>
                <div>
                    <h3 style="margin: 0 0 8px 0; font-size: 20px;">Неправильно</h3>
                    <p style="margin: 0;">Попробуй еще раз!</p>
                    ${data.show_hint && card.hint_text ? `<p style="margin: 8px 0 0 0;">💡 Подсказка: ${card.hint_text}</p>` : ''}
                    ${data.attempts_count ? `<p style="margin: 8px 0 0 0; font-size: 14px;">Попытка ${data.attempts_count}</p>` : ''}
                </div>
            </div>
        `;
        
        // Показываем подсказку
        if (data.show_hint && card.hint_text) {
            const hintBox = document.getElementById('hint-box');
            if (hintBox) {
                hintBox.innerHTML = `<strong>💡 Подсказка:</strong> ${card.hint_text}`;
                hintBox.classList.remove('hidden');
                hintBox.style.display = 'block';
            }
        }
        
        // Если много попыток, показываем правильный ответ
        if (data.attempts_count >= 2 && card.correct_answer) {
            const input = document.getElementById('spelling-input') || document.getElementById('writing-input');
            if (input) {
                input.value = card.correct_answer;
                input.style.borderColor = '#f59e0b';
                input.style.background = '#fef3c7';
            }
        }
    }
    
    // Кнопка пересдачи (если желтый статус или красный)
    if (data.card_status === 3 || data.card_status === 0) {
        setTimeout(() => {
            resultDiv.innerHTML += `
                <button class="btn-retry" onclick="retryCard()">
                    ${data.card_status === 3 ? 'Пересдать для получения зеленого статуса' : 'Попробовать еще раз'}
                </button>
            `;
        }, 2000);
    }
}

// Пересдача карточки
function retryCard() {
    cardCompleted = false;
    document.getElementById('result-message').classList.add('hidden');
    document.getElementById('hint-box').classList.add('hidden');
    document.getElementById('translation-box').classList.add('hidden');
    
    // Восстанавливаем интерфейс
    const options = document.querySelectorAll('.option');
    options.forEach(el => {
        el.classList.remove('disabled', 'correct', 'incorrect');
        el.onclick = function() {
            handleOptionClick(el.textContent.trim());
        };
    });
    
    const input = document.getElementById('spelling-input') || document.getElementById('writing-input');
    if (input) {
        input.disabled = false;
        input.value = '';
        input.style.borderColor = '';
        input.style.background = '';
    }
    
    const letterDivs = document.querySelectorAll('.spelling-letter');
    letterDivs.forEach(div => {
        div.style.cursor = 'pointer';
        div.style.opacity = '1';
        const letter = div.getAttribute('data-letter');
        const index = parseInt(div.getAttribute('data-index'));
        div.onclick = function() {
            addLetterToSpelling(letter, index);
        };
    });
    
    clearSpelling();
}

// Вспомогательные функции
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

function getCardTypeLabel(type) {
    const labels = {
        'repeat': 'Повторить', 'translate': 'Перевести', 'choose': 'Выбрать',
        'color': 'Цвет', 'speak': 'Проговорить', 'match': 'Сопоставить',
        'spelling': 'Написание', 'new_words': 'Новые слова', 'writing': 'Письмо'
    };
    return labels[type] || type;
}

function speakText(text) {
    if ('speechSynthesis' in window) {
        // Останавливаем предыдущую озвучку, если она идет
        speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 0.7; // Медленнее для лучшего понимания
        utterance.pitch = 1.0; // Немного ниже для более естественного звучания
        utterance.volume = 1.0;
        
        utterance.onerror = (event) => {
            console.error('Speech synthesis error:', event);
        };
        
        speechSynthesis.speak(utterance);
    } else {
        alert('Ваш браузер не поддерживает озвучку текста');
    }
}

// Распознавание речи для карточек repeat/speak
let recognition = null;
let isRecognizing = false;

async function startSpeechRecognition(correctAnswer) {
    if (cardCompleted) return;
    
    // Проверяем поддержку Web Speech API
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('Ваш браузер не поддерживает распознавание речи. Попробуйте использовать Chrome или Edge.');
        return;
    }
    
    // Проверяем и запрашиваем доступ к микрофону
    const statusEl = document.getElementById('recognition-status');
    const resultEl = document.getElementById('recognition-result');
    if (statusEl) {
        statusEl.innerHTML = '<span style="color: #667eea;">Проверяю доступ к микрофону...</span>';
    }
    
    try {
        // Запрашиваем разрешение на доступ к микрофону
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // Если получили доступ, останавливаем поток (он нам не нужен, только для проверки)
        stream.getTracks().forEach(track => track.stop());
        console.log('Microphone access granted');
    } catch (error) {
        console.error('Microphone access error:', error);
        let errorMessage = 'Не удалось получить доступ к микрофону. ';
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            errorMessage += 'Разрешите доступ к микрофону в настройках браузера (иконка замка рядом с адресом) и попробуйте снова.';
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
            errorMessage += 'Микрофон не найден. Убедитесь, что микрофон подключен.';
        } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
            errorMessage += 'Микрофон занят другим приложением. Закройте другие приложения, использующие микрофон.';
        } else {
            errorMessage += 'Ошибка: ' + error.message;
        }
        
        if (statusEl) {
            statusEl.innerHTML = `<span style="color: #ef4444; font-weight: 600;">${errorMessage}</span>`;
        }
        alert(errorMessage);
        return;
    }
    
    // Останавливаем предыдущее распознавание, если оно активно
    try {
        if (recognition && isRecognizing) {
            recognition.stop();
            isRecognizing = false;
        }
    } catch (e) {
        // Игнорируем ошибки при остановке
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    
    recognition.lang = 'en-US';
    recognition.continuous = true; // Включаем непрерывное распознавание для лучшего результата
    recognition.interimResults = true; // Включаем промежуточные результаты для лучшей обратной связи
    recognition.maxAlternatives = 1; // Используем только лучший вариант для упрощения
    
    console.log('Recognition settings:', {
        lang: recognition.lang,
        continuous: recognition.continuous,
        interimResults: recognition.interimResults,
        maxAlternatives: recognition.maxAlternatives
    });
    
    // Таймер для автоматической остановки через 10 секунд, если нет речи
    let noSpeechTimer = null;
    
    let expectedAnswers = [];
    const extraData = (cardData && cardData.extra_data) || {};
    if (cardData && extraData.words && Array.isArray(extraData.words) && extraData.words.length > 0) {
        expectedAnswers = extraData.words.map(w => String(w || '').toLowerCase().trim()).filter(w => w);
    } else if (correctAnswer) {
        expectedAnswers = [String(correctAnswer).toLowerCase().trim()];
    } else if (cardData && cardData.question_text) {
        expectedAnswers = [String(cardData.question_text).toLowerCase().trim()];
    }
    
    console.log('Starting recognition with expected answers:', expectedAnswers);
    
    recognition.onstart = () => {
        isRecognizing = true;
        console.log('Recognition started');
        if (statusEl) {
            statusEl.innerHTML = '<span style="color: #667eea; font-weight: 600;">🎤 Слушаю... Говори четко и громко!</span>';
        }
        if (resultEl) {
            resultEl.style.display = 'none';
            resultEl.textContent = '';
        }
        
        // Устанавливаем таймер на 10 секунд - если за это время нет речи, останавливаем
        noSpeechTimer = setTimeout(() => {
            if (isRecognizing && recognition) {
                console.log('No speech detected for 10 seconds, stopping recognition');
                try {
                    recognition.stop();
                } catch (e) {
                    console.error('Error stopping recognition:', e);
                }
            }
        }, 10000);
    };
    
    recognition.onresult = (event) => {
        console.log('Recognition result event:', event);
        console.log('Event results:', event.results);
        console.log('Results length:', event.results ? event.results.length : 0);
        
        // Очищаем таймер, так как речь обнаружена
        if (noSpeechTimer) {
            clearTimeout(noSpeechTimer);
            noSpeechTimer = null;
        }
        
        // Получаем финальный результат
        let transcript = '';
        let confidence = 0;
        let hasFinalResult = false;
        
        if (!event.results || event.results.length === 0) {
            console.error('No results in recognition event');
            return;
        }
        
        // Проходим по всем результатам
        for (let i = 0; i < event.results.length; i++) {
            const result = event.results[i];
            console.log(`Result ${i}:`, result, 'isFinal:', result.isFinal);
            
            if (result[0]) {
                const alternative = result[0];
                const altTranscript = alternative.transcript.trim();
                console.log(`Alternative ${i}:`, altTranscript, 'confidence:', alternative.confidence);
                
                if (result.isFinal) {
                    // Финальный результат - используем его
                    transcript = altTranscript;
                    confidence = alternative.confidence || 0;
                    hasFinalResult = true;
                    console.log('Final transcript found:', transcript);
                } else if (altTranscript) {
                    // Промежуточный результат - показываем пользователю
            if (resultEl) {
                resultEl.style.display = 'block';
                resultEl.textContent = `Слышу: "${altTranscript}"...`;
                resultEl.style.color = '#667eea';
                resultEl.style.background = '#eff6ff';
                resultEl.style.border = '2px solid #667eea';
                    }
                }
            }
        }
        
        // Если есть финальный результат, обрабатываем его
        if (hasFinalResult && transcript) {
            // Останавливаем распознавание, так как получили финальный результат
            try {
                recognition.stop();
            } catch (e) {
                console.error('Error stopping recognition:', e);
            }
            
            const transcriptLower = transcript.toLowerCase();
            console.log('Processing final transcript:', transcript, 'confidence:', confidence);
            console.log('Expected answers:', expectedAnswers);
            
            if (resultEl) {
                resultEl.style.display = 'block';
                resultEl.textContent = `Вы сказали: "${transcript}"`;
                resultEl.style.color = '#1f2937';
            }
            
            // Проверяем правильность (fuzzy matching) со всеми возможными ответами
            let isCorrect = false;
            if (expectedAnswers.length > 0) {
                for (const expected of expectedAnswers) {
                    const match = checkSpeechMatch(transcriptLower, expected);
                    console.log(`Checking "${transcriptLower}" against "${expected}":`, match);
                    if (match) {
                        isCorrect = true;
                        console.log('✓ Match found:', transcriptLower, 'matches', expected);
                        break;
                    }
                }
            } else {
                // Если нет ожидаемых ответов, считаем правильным (для карточек без проверки)
                isCorrect = true;
                console.log('No expected answers, marking as correct');
            }
            
            if (statusEl) {
                if (isCorrect) {
                    statusEl.innerHTML = '<span style="color: #22c55e; font-weight: 600;">✓ Правильно! Молодец!</span>';
                    if (resultEl) {
                        resultEl.style.background = '#f0fdf4';
                        resultEl.style.border = '2px solid #22c55e';
                    }
                } else {
                    statusEl.innerHTML = '<span style="color: #ef4444; font-weight: 600;">✗ Неправильно. Попробуй еще раз!</span>';
                    if (resultEl) {
                        resultEl.style.background = '#fef2f2';
                        resultEl.style.border = '2px solid #ef4444';
                    }
                }
            }
            
            // Отправляем ответ на сервер
            setTimeout(() => {
                submitAnswer(transcript, isCorrect);
            }, 1500);
        }
    };
    
    recognition.onerror = (event) => {
        isRecognizing = false;
        
        // Очищаем таймер
        if (noSpeechTimer) {
            clearTimeout(noSpeechTimer);
            noSpeechTimer = null;
        }
        
        console.error('Speech recognition error:', event.error);
        console.error('Error details:', event);
        
        let errorMessage = 'Ошибка распознавания. Попробуй еще раз.';
        if (event.error === 'no-speech') {
            errorMessage = 'Речь не распознана. Попробуйте:\n1. Проверьте, что микрофон включен\n2. Говорите громче и четче\n3. Подождите 2-3 секунды после нажатия кнопки\n4. Убедитесь, что микрофон не занят другим приложением';
        } else if (event.error === 'audio-capture') {
            errorMessage = 'Микрофон не найден. Проверьте настройки браузера и убедитесь, что микрофон подключен.';
        } else if (event.error === 'not-allowed') {
            errorMessage = 'Доступ к микрофону запрещен. Разрешите доступ в настройках браузера (иконка замка рядом с адресом).';
        } else if (event.error === 'network') {
            errorMessage = 'Ошибка сети. Проверьте подключение к интернету.';
        } else if (event.error === 'aborted') {
            // Игнорируем aborted - это нормально при остановке
            return;
        } else if (event.error === 'service-not-allowed') {
            errorMessage = 'Сервис распознавания недоступен. Попробуйте позже.';
        }
        
        console.error('Error message:', errorMessage);
        
        if (statusEl) {
            statusEl.innerHTML = `<span style="color: #ef4444; font-weight: 600;">${errorMessage}</span>`;
        }
        
        if (resultEl && event.error !== 'aborted') {
            resultEl.style.display = 'block';
            resultEl.textContent = `Ошибка: ${event.error}`;
            resultEl.style.background = '#fef2f2';
            resultEl.style.border = '2px solid #ef4444';
            resultEl.style.color = '#991b1b';
        }
        
        // Позволяем попробовать снова
        if (event.error !== 'aborted') {
            setTimeout(() => {
                if (statusEl && !statusEl.innerHTML.includes('Правильно') && !statusEl.innerHTML.includes('Неправильно')) {
                    statusEl.innerHTML = '<span style="color: #6b7280;">Нажмите кнопку "Начать запись" еще раз</span>';
                }
            }, 5000);
        }
    };
    
    recognition.onend = () => {
        isRecognizing = false;
        console.log('Recognition ended');
        
        // Очищаем таймер
        if (noSpeechTimer) {
            clearTimeout(noSpeechTimer);
            noSpeechTimer = null;
        }
        
        // Не меняем статус, если уже показан результат или ошибка
        if (statusEl && 
            !statusEl.innerHTML.includes('Правильно') && 
            !statusEl.innerHTML.includes('Неправильно') && 
            !statusEl.innerHTML.includes('Ошибка') &&
            !statusEl.innerHTML.includes('Речь не распознана') &&
            !statusEl.innerHTML.includes('Микрофон') &&
            !statusEl.innerHTML.includes('Доступ')) {
            statusEl.innerHTML = '<span style="color: #6b7280;">Запись завершена. Обрабатываю...</span>';
        }
    };
    
    // Останавливаем предыдущее распознавание, если оно активно
    try {
        if (recognition && isRecognizing) {
            recognition.stop();
        }
    } catch (e) {
        // Игнорируем ошибки при остановке
    }
    
    try {
        recognition.start();
    } catch (error) {
        console.error('Ошибка запуска распознавания:', error);
        isRecognizing = false;
        if (statusEl) {
            if (error.message && error.message.includes('already started')) {
                statusEl.innerHTML = '<span style="color: #ef4444;">Распознавание уже запущено. Подождите...</span>';
            } else {
                statusEl.innerHTML = '<span style="color: #ef4444;">Не удалось начать запись. Попробуй еще раз.</span>';
            }
        }
    }
}

// Проверка совпадения произнесенного текста с правильным ответом
function checkSpeechMatch(spoken, correct) {
    if (!spoken || !correct) return false;
    
    // Убираем знаки препинания и лишние пробелы
    const normalize = (text) => text.replace(/[.,!?;:'"]/g, '').replace(/\s+/g, ' ').trim().toLowerCase();
    
    spoken = normalize(spoken);
    correct = normalize(correct);
    
    // Точное совпадение
    if (spoken === correct) {
        return true;
    }
    
    // Проверка на включение правильного ответа (для длинных фраз)
    if (correct.length > 5 && spoken.includes(correct)) {
        return true;
    }
    
    // Проверка на включение произнесенного в правильный ответ
    if (spoken.length > 5 && correct.includes(spoken)) {
        return true;
    }
    
    // Для коротких фраз проверяем похожесть (например, "it's sunny" и "it sunny")
    const spokenWords = spoken.split(/\s+/).filter(w => w.length > 0);
    const correctWords = correct.split(/\s+/).filter(w => w.length > 0);
    
    if (spokenWords.length === 0 || correctWords.length === 0) {
        return false;
    }
    
    // Если большинство слов совпадает
    const matchingWords = spokenWords.filter(w => correctWords.includes(w));
    const matchRatio = matchingWords.length / Math.max(spokenWords.length, correctWords.length);
    if (matchRatio >= 0.7) {
        return true;
    }
    
    // Если количество слов совпадает или отличается на 1, проверяем более гибко
    if (Math.abs(spokenWords.length - correctWords.length) <= 1) {
        let matches = 0;
        for (const word of spokenWords) {
            if (correctWords.some(cw => cw === word || cw.includes(word) || word.includes(cw))) {
                matches++;
            }
        }
        const flexibleMatchRatio = matches / Math.max(spokenWords.length, correctWords.length);
        return flexibleMatchRatio >= 0.7;
    }
    
    return false;
}

// Функции для spelling (используем из lesson-spelling.js)
let spellingAnswers = [];

function addLetterToSpelling(letter, letterIndex) {
    const answerDiv = document.getElementById('spelling-answer');
    const letterDiv = document.querySelector(`.spelling-letter[data-index="${letterIndex}"]`);
    
    if (answerDiv && letterDiv && !letterDiv.classList.contains('used')) {
        spellingAnswers.push(letter);
        letterDiv.classList.add('used');
        letterDiv.style.opacity = '0.5';
        letterDiv.style.cursor = 'not-allowed';
        letterDiv.onclick = null;
        
        const letterSpan = document.createElement('span');
        letterSpan.className = 'spelling-answer-letter';
        letterSpan.textContent = letter.toUpperCase();
        letterSpan.style.cssText = `
            width: 50px; height: 50px; background: #22c55e; color: white;
            font-size: 24px; font-weight: bold; display: flex; align-items: center;
            justify-content: center; border-radius: 12px; cursor: pointer;
            transition: all 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        `;
        letterSpan.onclick = function() {
            removeLetterFromSpelling(letterIndex);
        };
        answerDiv.appendChild(letterSpan);
    }
}

function removeLetterFromSpelling(letterIndex) {
    const index = spellingAnswers.findIndex((_, idx) => {
        const letterDiv = document.querySelector(`.spelling-letter[data-index="${letterIndex}"]`);
        return letterDiv && !letterDiv.classList.contains('used');
    });
    
    if (index > -1) {
        spellingAnswers.splice(index, 1);
        
        const answerDiv = document.getElementById('spelling-answer');
        const letterDiv = document.querySelector(`.spelling-letter[data-index="${letterIndex}"]`);
        
        if (answerDiv && letterDiv) {
            const answerLetters = answerDiv.querySelectorAll('.spelling-answer-letter');
            if (answerLetters[index]) {
                answerLetters[index].remove();
            }
            
            letterDiv.classList.remove('used');
            letterDiv.style.opacity = '1';
            letterDiv.style.cursor = 'pointer';
            const letter = letterDiv.getAttribute('data-letter');
            const idx = parseInt(letterDiv.getAttribute('data-index'));
            letterDiv.onclick = function() {
                addLetterToSpelling(letter, idx);
            };
        }
    }
}

function clearSpelling() {
    spellingAnswers = [];
    const answerDiv = document.getElementById('spelling-answer');
    if (answerDiv) {
        answerDiv.innerHTML = '';
    }
    
    const letterDivs = document.querySelectorAll('.spelling-letter');
    letterDivs.forEach(div => {
        div.classList.remove('used');
        div.style.opacity = '1';
        div.style.cursor = 'pointer';
        const letter = div.getAttribute('data-letter');
        const index = parseInt(div.getAttribute('data-index'));
        div.onclick = function() {
            addLetterToSpelling(letter, index);
        };
    });
}

