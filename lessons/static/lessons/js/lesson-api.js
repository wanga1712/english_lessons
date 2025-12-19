/**
 * Модуль для работы с API
 * Размер: ~120 строк
 */

const LessonAPI = {
    /**
     * Загрузка прогресса пользователя
     */
    async loadUserProgress() {
        try {
            const response = await fetch('/api/progress/');
            if (response.ok) {
                return await response.json();
            }
            return { total_experience: 0, current_level: 1 };
        } catch (error) {
            console.error('Ошибка загрузки прогресса:', error);
            return { total_experience: 0, current_level: 1 };
        }
    },

    /**
     * Начало попытки урока
     */
    async startLessonAttempt(lessonId) {
        try {
            const response = await fetch(`/api/lessons/${lessonId}/start/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            if (response.ok) {
                const data = await response.json();
                return data.attempt_id;
            }
            return null;
        } catch (error) {
            console.error('Ошибка начала урока:', error);
            return null;
        }
    },

    /**
     * Отправка ответа на карточку
     */
    async submitCardAnswer(attemptId, cardId, answer, isCorrect) {
        try {
            const response = await fetch('/api/cards/answer/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    attempt_id: attemptId,
                    card_id: cardId,
                    answer: answer,
                    is_correct: isCorrect
                })
            });
            if (response.ok) {
                return await response.json();
            }
            return null;
        } catch (error) {
            console.error('Ошибка отправки ответа:', error);
            return null;
        }
    },

    /**
     * Завершение попытки урока
     */
    async completeLessonAttempt(attemptId) {
        try {
            const response = await fetch(`/api/attempts/${attemptId}/complete/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            if (response.ok) {
                return await response.json();
            }
            return null;
        } catch (error) {
            console.error('Ошибка завершения урока:', error);
            return null;
        }
    }
};

