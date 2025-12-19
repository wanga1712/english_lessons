/**
 * JavaScript для главной страницы
 * Размер: ~150 строк
 */

let progressInterval = null;
let timeInterval = null;
let currentProgress = 0;
let estimatedSeconds = 0;
let elapsedSeconds = 0;

const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (mins > 0) {
        return `${mins} мин ${secs} сек`;
    }
    return `${secs} сек`;
};

const updateProgressBar = (value, labelText) => {
    const fillEl = document.getElementById('progress-fill');
    const labelEl = document.getElementById('progress-label');

    if (!fillEl || !labelEl) {
        return;
    }

    const clamped = Math.max(0, Math.min(100, value));
    fillEl.style.width = clamped + '%';
    
    if (estimatedSeconds > 0 && elapsedSeconds < estimatedSeconds) {
        const remaining = estimatedSeconds - elapsedSeconds;
        labelEl.textContent = labelText ? `${labelText} (осталось ~${formatTime(remaining)})` : '';
    } else {
        labelEl.textContent = labelText || '';
    }
};

const startFakeProgress = (totalSeconds) => {
    currentProgress = 0;
    elapsedSeconds = 0;
    estimatedSeconds = totalSeconds || 120;
    updateProgressBar(0, 'Формирую для тебя урок...');

    if (progressInterval) {
        clearInterval(progressInterval);
    }
    if (timeInterval) {
        clearInterval(timeInterval);
    }

    timeInterval = setInterval(() => {
        elapsedSeconds++;
        if (elapsedSeconds >= estimatedSeconds) {
            elapsedSeconds = estimatedSeconds;
        }
    }, 1000);

    progressInterval = setInterval(() => {
        if (currentProgress < 88) {
            const step = currentProgress < 50 ? 2 : 1;
            currentProgress += step;
            updateProgressBar(currentProgress, 'Формирую для тебя урок...');
        }
    }, 350);
};

const finishProgress = (success, text) => {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
    if (timeInterval) {
        clearInterval(timeInterval);
        timeInterval = null;
    }

    if (success) {
        currentProgress = 100;
        updateProgressBar(100, 'Урок готов!');
    } else {
        currentProgress = 0;
        estimatedSeconds = 0;
        elapsedSeconds = 0;
        updateProgressBar(0, '');
    }

    const statusEl = document.getElementById('status');
    if (statusEl) {
        statusEl.textContent = text;
    }
};

const handleClickNewLesson = async () => {
    const button = document.getElementById('new-lesson-btn');
    const statusEl = document.getElementById('status');

    if (!button || !statusEl) {
        return;
    }

    button.disabled = true;
    statusEl.textContent = 'Обработка видео... Это может занять несколько минут при первом запуске.';

    try {
        const infoResponse = await fetch('/api/videos/next_pending_info/', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            },
        });

        let estimatedTime = 120;
        if (infoResponse.ok) {
            const infoData = await infoResponse.json();
            estimatedTime = infoData.estimated_seconds || 120;
        }

        startFakeProgress(estimatedTime);

        const response = await fetch('/api/videos/process_next/', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
            },
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const message = errorData.error || 'Ошибка обработки видео';
            finishProgress(false, message);
            button.disabled = false;
            return;
        }

        const data = await response.json();
        const message = `Урок создан: "${data.lesson_title}" (карточек: ${data.cards_count})`;
        finishProgress(true, message);
        button.disabled = false;
        
        const lessonLinkDiv = document.getElementById('last-lesson-link');
        const lessonLinkContent = document.getElementById('lesson-link-content');
        if (lessonLinkDiv && lessonLinkContent) {
            lessonLinkContent.innerHTML = `
                <a href="/lesson/${data.lesson_id}/" style="color: #667eea; text-decoration: underline; font-weight: 600;">
                    🎯 Открыть урок "${data.lesson_title}" (${data.cards_count} карточек)
                </a>
            `;
            lessonLinkDiv.style.display = 'block';
        }
        
        loadLessons();
    } catch (error) {
        finishProgress(false, 'Ошибка сети или сервера при обработке видео.');
        button.disabled = false;
    }
};

const loadLessons = async () => {
    const container = document.getElementById('lessons-container');
    if (!container) return;
    
    try {
        const response = await fetch('/api/lessons/');
        const data = await response.json();
        
        if (data.lessons && data.lessons.length > 0) {
            container.style.display = 'grid';
            container.style.gridTemplateColumns = 'repeat(auto-fill, minmax(300px, 1fr))';
            container.style.gap = '20px';
            
            container.innerHTML = data.lessons.map((lesson, index) => {
                const progress = lesson.progress || {};
                const completionPercent = progress.completion_percent || 0;
                const topicsCompleted = progress.topics_completed || 0;
                const topicsTotal = progress.topics_total || lesson.topics_count || 0;
                const cardsCompleted = progress.cards_completed || 0;
                const cardsTotal = progress.cards_total || lesson.cards_count || 0;
                
                // Определяем цвет прогресса
                let progressColor = '#e9ecef';
                if (completionPercent >= 80) progressColor = '#22c55e';
                else if (completionPercent >= 50) progressColor = '#f59e0b';
                else if (completionPercent > 0) progressColor = '#ef4444';
                
                return `
                <div class="lesson-card" onclick="window.location.href='/lesson/${lesson.id}/'" 
                     style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                            border-radius: 16px; padding: 24px; cursor: pointer;
                            transition: all 0.3s; border: 2px solid #e9ecef;
                            position: relative; overflow: hidden;">
                    <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px;
                                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                                transform: scaleX(1); transition: transform 0.3s;" 
                         class="lesson-card-bar"></div>
                    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
                        <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    border-radius: 50%; display: flex; align-items: center; justify-content: center;
                                    font-size: 32px; font-weight: bold; color: white; flex-shrink: 0;">
                            ${index + 1}
                        </div>
                        <div style="flex: 1;">
                            <h3 style="margin: 0 0 4px 0; font-size: 20px; font-weight: 700; color: #1f2937;">${lesson.title}</h3>
                            <p style="margin: 0; color: #6b7280; font-size: 14px;">${lesson.description || ''}</p>
                        </div>
                    </div>
                    ${completionPercent > 0 ? `
                        <div style="margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                <span style="font-size: 12px; font-weight: 600; color: #6b7280;">Прогресс</span>
                                <span style="font-size: 12px; font-weight: 700; color: ${progressColor};">${completionPercent}%</span>
                            </div>
                            <div style="width: 100%; height: 8px; background: #e9ecef; border-radius: 4px; overflow: hidden;">
                                <div style="width: ${completionPercent}%; height: 100%; background: ${progressColor}; transition: width 0.3s;"></div>
                            </div>
                        </div>
                    ` : ''}
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 16px; padding-top: 16px; border-top: 1px solid #e9ecef;">
                        <div style="color: #6b7280; font-size: 14px;">
                            📚 ${cardsCompleted}/${cardsTotal} карточек
                            ${topicsTotal > 0 ? ` • 🎯 ${topicsCompleted}/${topicsTotal} тем` : ''}
                        </div>
                        <div style="color: #667eea; font-weight: 600; font-size: 14px;">→</div>
                    </div>
                    ${lesson.video_id ? `
                        <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e9ecef;">
                            <button onclick="event.stopPropagation(); recreateLesson(${lesson.video_id}, ${lesson.id})" 
                                    style="width: 100%; background: #f59e0b; color: white; padding: 10px;
                                           border-radius: 10px; border: none; cursor: pointer; font-weight: 600;
                                           font-size: 14px; transition: all 0.3s; box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);"
                                    onmouseover="this.style.background='#d97706'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(245, 158, 11, 0.4)';" 
                                    onmouseout="this.style.background='#f59e0b'; this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(245, 158, 11, 0.3)';"
                                    title="Пересоздать урок с новыми улучшениями">
                                🔄 Пересоздать урок
                            </button>
                        </div>
                    ` : ''}
                </div>
            `;
            }).join('');
            
            // Добавляем hover эффекты
            container.querySelectorAll('.lesson-card').forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-4px)';
                    this.style.boxShadow = '0 8px 24px rgba(102, 126, 234, 0.3)';
                    this.style.borderColor = '#667eea';
                    const bar = this.querySelector('.lesson-card-bar');
                    if (bar) bar.style.transform = 'scaleX(1)';
                });
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                    this.style.boxShadow = 'none';
                    this.style.borderColor = '#e9ecef';
                    const bar = this.querySelector('.lesson-card-bar');
                    if (bar) bar.style.transform = 'scaleX(0)';
                });
            });
        } else {
            container.innerHTML = '<p style="color: #6b7280;">Уроков пока нет. Создайте первый урок!</p>';
        }
    } catch (error) {
        container.innerHTML = '<p style="color: #dc2626;">Ошибка загрузки уроков</p>';
    }
};

const recreateLesson = async (videoId, lessonId) => {
    if (!confirm('Пересоздать урок? Старый урок будет удалён, включая все карточки и прогресс. Это действие нельзя отменить.')) {
        return;
    }
    
    const statusEl = document.getElementById('status');
    if (statusEl) {
        statusEl.textContent = 'Пересоздание урока... Это может занять несколько минут.';
    }
    
    try {
        const response = await fetch(`/api/videos/${videoId}/process/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            body: JSON.stringify({ force_recreate: true })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const message = errorData.error || 'Ошибка пересоздания урока';
            if (statusEl) {
                statusEl.textContent = `Ошибка: ${message}`;
            }
            alert(`Ошибка: ${message}`);
            return;
        }
        
        const data = await response.json();
        const message = `Урок пересоздан: "${data.lesson_title}" (карточек: ${data.cards_count})`;
        if (statusEl) {
            statusEl.textContent = message;
        }
        
        // Обновляем список уроков
        loadLessons();
        
        // Показываем ссылку на новый урок
        const lessonLinkDiv = document.getElementById('last-lesson-link');
        const lessonLinkContent = document.getElementById('lesson-link-content');
        if (lessonLinkDiv && lessonLinkContent) {
            lessonLinkContent.innerHTML = `
                <a href="/lesson/${data.lesson_id}/" style="color: #667eea; text-decoration: underline; font-weight: 600;">
                    🎯 Открыть пересозданный урок "${data.lesson_title}" (${data.cards_count} карточек)
                </a>
            `;
            lessonLinkDiv.style.display = 'block';
        }
        
    } catch (error) {
        const errorMsg = 'Ошибка сети или сервера при пересоздании урока.';
        if (statusEl) {
            statusEl.textContent = errorMsg;
        }
        alert(errorMsg);
    }
};

const handleProcessAll = async () => {
    const button = document.getElementById('process-all-btn');
    const statusEl = document.getElementById('status');
    
    if (!button || !statusEl) {
        return;
    }
    
    if (!confirm('Обработать все необработанные видео? Это может занять много времени.')) {
        return;
    }
    
    button.disabled = true;
    statusEl.textContent = 'Запуск обработки всех видео...';
    
    // Запускаем отслеживание статуса сразу
    startProcessingStatusCheck();
    
    try {
        // Запускаем обработку (она будет идти на сервере)
        const response = await fetch('/api/videos/process_all/', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
            },
        });
        
        if (!response.ok) {
            stopProcessingStatusCheck();
            const errorData = await response.json().catch(() => ({}));
            const message = errorData.error || 'Ошибка обработки видео';
            statusEl.textContent = `Ошибка: ${message}`;
            statusEl.style.color = '#dc2626';
            button.disabled = false;
            return;
        }
        
        // Обработка запущена, статус будет обновляться через checkProcessingStatus
        // Не ждем завершения, продолжаем отслеживать статус
        button.disabled = false;
        
    } catch (error) {
        stopProcessingStatusCheck();
        statusEl.textContent = 'Ошибка сети или сервера при запуске обработки видео.';
        statusEl.style.color = '#dc2626';
        button.disabled = false;
    }
};

const updateUserStats = async () => {
    try {
        const response = await fetch('/api/progress/');
        if (response.ok) {
            const progress = await response.json();
            const levelEl = document.getElementById('user-level');
            const xpEl = document.getElementById('user-xp');
            const scoreEl = document.getElementById('user-score');
            
            if (levelEl) levelEl.textContent = progress.current_level || 1;
            if (xpEl) xpEl.textContent = progress.total_experience || 0;
            
            // Получаем рейтинг из аватара
            if (scoreEl) {
                // Можно добавить отдельный API для получения рейтинга
                // Пока используем значение из шаблона или обновляем через другой запрос
            }
        }
    } catch (error) {
        console.error('Ошибка обновления статистики:', error);
    }
};

// Отслеживание статуса обработки видео
let processingStatusInterval = null;
let lastLogCount = 0;

const updateLogsDisplay = (logs) => {
    const logsContainer = document.getElementById('processing-logs');
    const logsContent = document.getElementById('logs-content');
    
    if (!logsContainer || !logsContent) return;
    
    if (logs && logs.length > 0) {
        logsContainer.style.display = 'block';
        
        // Показываем только новые логи
        const newLogs = logs.slice(lastLogCount);
        lastLogCount = logs.length;
        
        newLogs.forEach(log => {
            const logLine = document.createElement('div');
            logLine.style.marginBottom = '4px';
            logLine.style.padding = '2px 0';
            
            // Цвет в зависимости от уровня
            let color = '#374151';
            if (log.level === 'ERROR' || log.level === 'CRITICAL') {
                color = '#dc2626';
            } else if (log.level === 'WARNING') {
                color = '#f59e0b';
            } else if (log.level === 'INFO') {
                color = '#2563eb';
            } else if (log.level === 'DEBUG') {
                color = '#6b7280';
            }
            
            logLine.style.color = color;
            
            // Форматируем время
            const time = new Date(log.timestamp).toLocaleTimeString('ru-RU');
            const message = log.message.replace(/\[INFO\]|\[DEBUG\]|\[WARNING\]|\[ERROR\]/g, '').trim();
            
            logLine.textContent = `[${time}] ${message}`;
            logsContent.appendChild(logLine);
        });
        
        // Автопрокрутка вниз
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }
};

const checkProcessingStatus = async () => {
    try {
        const response = await fetch('/api/videos/processing_status/');
        if (!response.ok) return;
        
        const data = await response.json();
        const statusEl = document.getElementById('status');
        
        // Обновляем логи
        if (data.logs) {
            updateLogsDisplay(data.logs);
        }
        
        if (data.is_processing && statusEl) {
            let statusText = '';
            if (data.current_video) {
                const msg = data.current_video.processing_message || '';
                statusText = `Идет обработка видео ${data.current_video.index}/${data.current_video.total}: ${data.current_video.file_name}`;
                if (msg) {
                    statusText += ` - ${msg}`;
                }
            } else if (data.processing > 0) {
                statusText = `Идет обработка... (обработано: ${data.done}/${data.total_videos})`;
            } else if (data.pending > 0) {
                statusText = `Ожидание обработки... (в очереди: ${data.pending})`;
            }
            
            if (statusText) {
                statusEl.textContent = statusText;
                statusEl.style.color = '#667eea';
                statusEl.style.fontWeight = '600';
            }
            
            // Обновляем список уроков, если появились новые
            if (data.done > 0) {
                loadLessons();
            }
        } else if (statusEl && !statusEl.textContent.includes('Ошибка') && !statusEl.textContent.includes('успешно')) {
            // Если обработка завершена и нет сообщения об ошибке/успехе, очищаем статус
            if (data.done === data.total_videos && data.total_videos > 0) {
                statusEl.textContent = '';
            }
        }
    } catch (error) {
        console.error('Ошибка проверки статуса обработки:', error);
    }
};

const startProcessingStatusCheck = () => {
    // Проверяем статус каждые 3 секунды
    if (processingStatusInterval) {
        clearInterval(processingStatusInterval);
    }
    processingStatusInterval = setInterval(checkProcessingStatus, 3000);
    // Проверяем сразу
    checkProcessingStatus();
};

const stopProcessingStatusCheck = () => {
    if (processingStatusInterval) {
        clearInterval(processingStatusInterval);
        processingStatusInterval = null;
    }
};

const initHomePage = () => {
    const button = document.getElementById('new-lesson-btn');
    if (button) {
        button.addEventListener('click', handleClickNewLesson);
    }
    
    const processAllBtn = document.getElementById('process-all-btn');
    if (processAllBtn) {
        processAllBtn.addEventListener('click', () => {
            handleProcessAll();
            startProcessingStatusCheck();
        });
    }
    
    const recreateAllBtn = document.getElementById('recreate-all-lessons-btn');
    if (recreateAllBtn) {
        recreateAllBtn.addEventListener('click', () => {
            handleRecreateAllLessons();
            startProcessingStatusCheck();
        });
    }
    
    updateUserStats();
    loadLessons();
    
    // Запускаем проверку статуса обработки
    startProcessingStatusCheck();
    
    // Кнопка очистки логов
    const clearLogsBtn = document.getElementById('clear-logs-btn');
    if (clearLogsBtn) {
        clearLogsBtn.addEventListener('click', () => {
            const logsContent = document.getElementById('logs-content');
            if (logsContent) {
                logsContent.innerHTML = '';
                lastLogCount = 0;
            }
        });
    }
    
    // Обновляем статистику каждые 30 секунд
    setInterval(updateUserStats, 30000);
};

const handleRecreateAllLessons = async () => {
    if (!confirm('ВНИМАНИЕ! Это действие удалит ВСЕ существующие уроки и пересоздаст их заново из всех видео файлов. Это может занять много времени. Продолжить?')) {
        return;
    }
    
    if (!confirm('Вы уверены? Все уроки, карточки и прогресс будут удалены и созданы заново. Это действие нельзя отменить!')) {
        return;
    }
    
    const button = document.getElementById('recreate-all-lessons-btn');
    const statusEl = document.getElementById('status');
    
    if (!button || !statusEl) {
        return;
    }
    
    button.disabled = true;
    statusEl.textContent = 'Запуск пересоздания всех уроков...';
    
    // Запускаем отслеживание статуса сразу
    startProcessingStatusCheck();
    
    try {
        // Запускаем пересоздание (оно будет идти на сервере)
        const response = await fetch('/api/videos/recreate_all_lessons/', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
            },
        });
        
        if (!response.ok) {
            stopProcessingStatusCheck();
            const errorData = await response.json().catch(() => ({}));
            const message = errorData.error || 'Ошибка пересоздания уроков';
            statusEl.textContent = `Ошибка: ${message}`;
            statusEl.style.color = '#dc2626';
            button.disabled = false;
            return;
        }
        
        // Пересоздание запущено, статус будет обновляться через checkProcessingStatus
        // Не ждем завершения, продолжаем отслеживать статус
        button.disabled = false;
        
    } catch (error) {
        stopProcessingStatusCheck();
        statusEl.textContent = 'Ошибка сети или сервера при запуске пересоздания уроков.';
        statusEl.style.color = '#dc2626';
        button.disabled = false;
    }
};

document.addEventListener('DOMContentLoaded', initHomePage);

