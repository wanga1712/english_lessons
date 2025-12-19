"""
Кастомный handler для логирования в интерфейс
"""
import logging
from lessons.services.log_storage import LogStorage


class InterfaceLogHandler(logging.Handler):
    """Handler для сохранения логов в хранилище для отображения в интерфейсе"""
    
    def __init__(self):
        super().__init__()
        self.log_storage = LogStorage.get_instance()
    
    def emit(self, record):
        """Сохранить лог в хранилище"""
        try:
            # Форматируем сообщение
            msg = self.format(record)
            # Сохраняем в хранилище
            self.log_storage.add_log(
                level=record.levelname,
                message=msg,
                source=record.name
            )
        except Exception:
            # Игнорируем ошибки при логировании, чтобы не создавать бесконечный цикл
            pass

