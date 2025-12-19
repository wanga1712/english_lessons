/**
 * Основной модуль для работы с уроком
 * Размер: ~140 строк
 * Требует: lesson-api.js, lesson-spelling.js, lesson-render.js
 */

window.LessonApp = {
        currentCardIndex: 0,
        attemptId: null,
        userProgress: { total_experience: 0, current_level: 1 },
        cardsData: typeof cardsData !== 'undefined' ? cardsData : [],
        topicsData: typeof topicsData !== 'undefined' ? topicsData : {},
        topicsList: typeof topicsList !== 'undefined' ? topicsList : [],
        currentTopic: null,
        filteredCardsData: [],
        lessonId: typeof lessonId !== 'undefined' ? lessonId : null,

        /**
         * Инициализация приложения
         */
        async init() {
            this.userProgress = await LessonAPI.loadUserProgress();
            this.updateUserStats();
            
            if (this.lessonId) {
                this.attemptId = await LessonAPI.startLessonAttempt(this.lessonId);
            }
            
            // Если есть несколько тем, показываем выбор темы
            if (this.topicsList && this.topicsList.length > 1) {
                this.initTopicsSelector();
            } else {
                // Если одна тема или нет тем, используем все карточки
                this.currentTopic = this.topicsList.length === 1 ? this.topicsList[0] : null;
                this.filteredCardsData = this.cardsData;
                this.renderCard();
            }
        },

        /**
         * Инициализация селектора тем
         */
        initTopicsSelector() {
            const selector = document.getElementById('topics-selector');
            const buttonsContainer = document.getElementById('topics-buttons');
            
            if (!selector || !buttonsContainer) return;
            
            selector.style.display = 'block';
            
            // Создаём кнопки для каждой темы
            const topicNames = {
                'weather': '🌤️ Погода',
                'actions': '🏃 Действия',
                'colors': '🎨 Цвета',
                'animals': '🐾 Животные',
                'food': '🍎 Еда',
                'family': '👨‍👩‍👧 Семья',
                'body': '👤 Части тела',
                'numbers': '🔢 Числа',
                'general': '📚 Общее'
            };
            
            this.topicsList.forEach(topic => {
                const button = document.createElement('button');
                const topicName = topicNames[topic] || topic;
                const cardCount = this.topicsData[topic] ? this.topicsData[topic].length : 0;
                
                button.textContent = `${topicName} (${cardCount} карточек)`;
                button.className = 'topic-button';
                button.style.cssText = `
                    padding: 12px 24px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s;
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
                `;
                
                button.onmouseover = () => {
                    button.style.transform = 'translateY(-2px)';
                    button.style.boxShadow = '0 6px 16px rgba(102, 126, 234, 0.4)';
                };
                button.onmouseout = () => {
                    button.style.transform = 'translateY(0)';
                    button.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.3)';
                };
                
                button.onclick = () => {
                    this.selectTopic(topic);
                };
                
                buttonsContainer.appendChild(button);
            });
        },

        /**
         * Выбор темы
         */
        selectTopic(topic) {
            this.currentTopic = topic;
            this.filteredCardsData = this.topicsData[topic] || [];
            this.currentCardIndex = 0;
            
            // Скрываем селектор тем
            const selector = document.getElementById('topics-selector');
            if (selector) {
                selector.style.display = 'none';
            }
            
            // Показываем контейнер карточек
            const cardContainer = document.getElementById('card-container');
            if (cardContainer) {
                cardContainer.style.display = 'block';
            }
            
            this.renderCard();
        },

        /**
         * Обновление статистики пользователя
         */
        updateUserStats() {
            const expEl = document.getElementById('experience');
            const levelEl = document.getElementById('level');
            if (expEl) expEl.textContent = this.userProgress.total_experience || 0;
            if (levelEl) levelEl.textContent = this.userProgress.current_level || 1;
        },

        /**
         * Отрисовка карточки
         */
        renderCard() {
            if (this.currentCardIndex >= this.filteredCardsData.length) {
                this.showCompletionScreen();
                return;
            }
            
            SpellingModule.cleanup(this.currentCardIndex - 1);
            
            const card = this.filteredCardsData[this.currentCardIndex];
            const container = document.getElementById('card-container');
            
            if (container && CardRenderer) {
                container.innerHTML = CardRenderer.renderCard(
                    card,
                    this.currentCardIndex,
                    this.filteredCardsData.length
                );
            }
            
            this.updateProgress();
        },

        /**
         * Обработка клика по варианту ответа
         */
        async handleOptionClick(index, userAnswer) {
            await this.submitAnswer(userAnswer, false);
        },

        /**
         * Обработка отправки ответа для writing
         */
        async handleSpellingSubmit(cardIndex, correctAnswer) {
            const input = document.getElementById(`spelling-input-${cardIndex}`);
            if (!input) return;
            
            const userAnswer = input.value.trim().toLowerCase();
            const isCorrect = userAnswer === correctAnswer.toLowerCase();
            await this.submitAnswer(userAnswer, isCorrect);
        },

        /**
         * Общая функция отправки ответа
         */
        async submitAnswer(userAnswer, isCorrectPrechecked = false) {
            const card = this.filteredCardsData[this.currentCardIndex];
            const optionElements = document.querySelectorAll('.option');
            
            let isCorrect = isCorrectPrechecked;
            if (!isCorrectPrechecked) {
                isCorrect = userAnswer === card.correct_answer || 
                           userAnswer.toLowerCase() === card.correct_answer?.toLowerCase();
            }
            
            // Отключаем интерфейс
            optionElements.forEach(el => el.classList.add('disabled'));
            const input = document.getElementById(`spelling-input-${this.currentCardIndex}`);
            if (input) {
                input.disabled = true;
                input.style.borderColor = isCorrect ? '#22c55e' : '#ef4444';
                input.style.background = isCorrect ? '#f0fdf4' : '#fef2f2';
            }
            
            const letterDivs = document.querySelectorAll(`#spelling-letters-${this.currentCardIndex} .spelling-letter`);
            letterDivs.forEach(div => {
                div.style.cursor = 'not-allowed';
                div.style.opacity = '0.6';
                div.onclick = null;
            });
            
            const checkButton = document.querySelector(`button[onclick*="checkSpelling(${this.currentCardIndex}"]`);
            const clearButton = document.querySelector(`button[onclick*="clearSpelling(${this.currentCardIndex}"]`);
            if (checkButton) checkButton.disabled = true;
            if (clearButton) clearButton.disabled = true;
            
            // Подсвечиваем ответ
            if (optionElements.length > 0 && !isCorrectPrechecked) {
                const clickedIndex = Array.from(optionElements).findIndex(el => 
                    el.textContent.trim() === userAnswer || 
                    el.textContent.trim().toLowerCase() === userAnswer.toLowerCase()
                );
                if (clickedIndex >= 0) {
                    optionElements[clickedIndex].classList.add(isCorrect ? 'correct' : 'incorrect');
                }
            }
            
            // Отправляем на сервер
            const data = await LessonAPI.submitCardAnswer(
                this.attemptId,
                card.id,
                userAnswer,
                isCorrect
            );
            
            if (data) {
                if (data.total_experience !== undefined) {
                    this.userProgress.total_experience = data.total_experience;
                    this.userProgress.current_level = data.current_level;
                    this.updateUserStats();
                }
                
                if (isCorrect) {
                    this.showPraise();
                    
                    if (card.translation_text) {
                        const translationBox = document.getElementById(`translation-box-${this.currentCardIndex}`);
                        if (translationBox) {
                            translationBox.innerHTML = `<strong>Перевод:</strong> ${card.translation_text}`;
                            translationBox.classList.remove('hidden');
                        }
                    }
                    
                    setTimeout(() => {
                        this.currentCardIndex++;
                        this.renderCard();
                    }, 2000);
                } else {
                    if (data.show_hint && card.hint_text) {
                        const hintBox = document.getElementById(`hint-box-${this.currentCardIndex}`);
                        if (hintBox) {
                            hintBox.innerHTML = `<strong>💡 Подсказка:</strong> ${card.hint_text}`;
                            hintBox.classList.remove('hidden');
                        }
                    }
                    
                    if ((card.card_type === 'spelling' || card.card_type === 'writing') && data.attempts_count >= 2) {
                        const input = document.getElementById(`spelling-input-${this.currentCardIndex}`);
                        if (input) {
                            input.value = card.correct_answer;
                            input.style.borderColor = '#f59e0b';
                            input.style.background = '#fef3c7';
                        }
                    }
                }
            }
        },

        /**
         * Озвучка текста
         */
        speakText(text) {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'en-US';
                utterance.rate = 0.9;
                utterance.pitch = 1.1;
                speechSynthesis.speak(utterance);
            } else {
                alert('Ваш браузер не поддерживает озвучку');
            }
        },

        /**
         * Показ похвалы
         */
        showPraise() {
            const praises = ['Отлично!', 'Молодец!', 'Правильно!', 'Супер!', 'Великолепно!'];
            const randomPraise = praises[Math.floor(Math.random() * praises.length)];
            
            const praiseDiv = document.createElement('div');
            praiseDiv.className = 'praise-message';
            praiseDiv.innerHTML = `
                <h2>🎉 ${randomPraise}</h2>
                <p>Ты правильно ответил!</p>
            `;
            document.body.appendChild(praiseDiv);
            
            setTimeout(() => {
                praiseDiv.remove();
            }, 1500);
        },

        /**
         * Обновление прогресс-бара
         */
        updateProgress() {
            const progress = (this.currentCardIndex / this.filteredCardsData.length) * 100;
            const progressFill = document.getElementById('progress-fill');
            if (progressFill) {
                progressFill.style.width = progress + '%';
            }
        },

        /**
         * Показ экрана завершения
         */
        async showCompletionScreen() {
            const cardContainer = document.getElementById('card-container');
            const completionScreen = document.getElementById('completion-screen');
            
            if (cardContainer) cardContainer.classList.add('hidden');
            if (completionScreen) completionScreen.classList.remove('hidden');
            
            if (this.attemptId) {
                const data = await LessonAPI.completeLessonAttempt(this.attemptId);
                if (data) {
                    const scoreEl = document.getElementById('final-score');
                    const correctEl = document.getElementById('correct-count');
                    const totalEl = document.getElementById('total-count');
                    
                    if (scoreEl) scoreEl.textContent = Math.round(data.score) + '%';
                    if (correctEl) correctEl.textContent = data.correct_cards;
                    if (totalEl) totalEl.textContent = data.total_cards;
                }
            }
        }
    };

// Инициализация при загрузке страницы
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => window.LessonApp.init());
} else {
    window.LessonApp.init();
}

