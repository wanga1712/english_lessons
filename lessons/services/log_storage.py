"""
Хранилище логов для отображения в интерфейсе
"""
import threading
from datetime import datetime
from collections import deque

class LogStorage:
    """Потокобезопасное хранилище логов в памяти"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self, max_logs=1000):
        self.logs = deque(maxlen=max_logs)
        self.lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def add_log(self, level, message, source='system'):
        """Добавить лог"""
        with self.lock:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'level': level,
                'message': message,
                'source': source
            }
            self.logs.append(log_entry)
    
    def get_logs(self, limit=100, since=None):
        """Получить логи"""
        with self.lock:
            logs_list = list(self.logs)
            if since:
                # Фильтруем по времени (если нужно)
                logs_list = [log for log in logs_list if log['timestamp'] > since]
            return logs_list[-limit:]
    
    def clear(self):
        """Очистить логи"""
        with self.lock:
            self.logs.clear()

