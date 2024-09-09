import logging
import queue
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener

# Настройка очереди и логгера
log_queue = queue.Queue()
queue_handler = QueueHandler(log_queue)

# Основной логгер
logger = logging.getLogger('rotating_threaded_logger')
logger.setLevel(logging.DEBUG)

# Обработчик с ротацией файлов по размеру
rotating_handler = RotatingFileHandler('app.log', maxBytes=1024 * 1024, backupCount=3)  # Увеличенный размер для тестирования
rotating_handler.setLevel(logging.DEBUG)

# Формат для логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rotating_handler.setFormatter(formatter)

# Слушатель очереди
listener = QueueListener(log_queue, rotating_handler)

# Добавляем обработчик очереди к логгеру
logger.addHandler(queue_handler)

# Запускаем слушатель из основного файла
def start_listener():
    listener.start()

def stop_listener():
    listener.stop()
