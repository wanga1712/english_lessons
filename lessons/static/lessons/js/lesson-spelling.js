/**
 * Модуль для работы с карточками типа spelling
 * Размер: ~140 строк
 */

const SpellingModule = {
    answers: {},

    /**
     * Добавление буквы к слову
     */
    addLetter(cardIndex, letter, letterIndex) {
        if (!this.answers[cardIndex]) {
            this.answers[cardIndex] = [];
        }
        
        const answerDiv = document.getElementById(`spelling-answer-${cardIndex}`);
        const letterDiv = document.querySelector(`#spelling-letters-${cardIndex} .spelling-letter[data-index="${letterIndex}"]`);
        
        if (answerDiv && letterDiv && !letterDiv.classList.contains('used')) {
            this.answers[cardIndex].push(letter);
            letterDiv.classList.add('used');
            letterDiv.style.opacity = '0.5';
            letterDiv.style.cursor = 'not-allowed';
            letterDiv.onclick = null;
            
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
            letterSpan.onclick = () => this.removeLetter(cardIndex, letterIndex, letter);
            answerDiv.appendChild(letterSpan);
        }
    },

    /**
     * Удаление буквы из слова
     */
    removeLetter(cardIndex, letterIndex, letter) {
        if (!this.answers[cardIndex]) return;
        
        const index = this.answers[cardIndex].indexOf(letter);
        if (index > -1) {
            this.answers[cardIndex].splice(index, 1);
            
            const answerDiv = document.getElementById(`spelling-answer-${cardIndex}`);
            const letterDiv = document.querySelector(`#spelling-letters-${cardIndex} .spelling-letter[data-index="${letterIndex}"]`);
            
            if (answerDiv && letterDiv) {
                const answerLetters = answerDiv.querySelectorAll('.spelling-answer-letter');
                if (answerLetters[index]) {
                    answerLetters[index].remove();
                }
                
                letterDiv.classList.remove('used');
                letterDiv.style.opacity = '1';
                letterDiv.style.cursor = 'pointer';
                letterDiv.onclick = () => this.addLetter(cardIndex, letter, letterIndex);
            }
        }
    },

    /**
     * Очистка собранного слова
     */
    clear(cardIndex) {
        this.answers[cardIndex] = [];
        const answerDiv = document.getElementById(`spelling-answer-${cardIndex}`);
        if (answerDiv) {
            answerDiv.innerHTML = '';
        }
        
        const letterDivs = document.querySelectorAll(`#spelling-letters-${cardIndex} .spelling-letter`);
        letterDivs.forEach(div => {
            div.classList.remove('used');
            div.style.opacity = '1';
            div.style.cursor = 'pointer';
            const letter = div.getAttribute('data-letter');
            const index = parseInt(div.getAttribute('data-index'));
            div.onclick = () => this.addLetter(cardIndex, letter, index);
        });
    },

    /**
     * Получение собранного слова
     */
    getAnswer(cardIndex) {
        return (this.answers[cardIndex] || []).join('').toLowerCase();
    },

    /**
     * Очистка данных для карточки
     */
    cleanup(cardIndex) {
        if (this.answers[cardIndex] !== undefined) {
            delete this.answers[cardIndex];
        }
    }
};

// Глобальные функции для использования в HTML
window.addLetterToSpelling = (cardIndex, letter, letterIndex) => {
    SpellingModule.addLetter(cardIndex, letter, letterIndex);
};

window.clearSpelling = (cardIndex) => {
    SpellingModule.clear(cardIndex);
};

window.checkSpelling = async (cardIndex, correctAnswer) => {
    const userAnswer = SpellingModule.getAnswer(cardIndex);
    const isCorrect = userAnswer === correctAnswer.toLowerCase();
    
    const answerDiv = document.getElementById(`spelling-answer-${cardIndex}`);
    if (answerDiv) {
        if (isCorrect) {
            answerDiv.style.borderColor = '#22c55e';
            answerDiv.style.background = '#f0fdf4';
        } else {
            answerDiv.style.borderColor = '#ef4444';
            answerDiv.style.background = '#fef2f2';
        }
    }
    
    if (window.LessonApp) {
        await window.LessonApp.submitAnswer(userAnswer, isCorrect);
    }
};

