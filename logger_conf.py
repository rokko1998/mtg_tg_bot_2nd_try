import logging
import queue
import os
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener

# Настройка очереди и логгера
log_queue = queue.Queue()
queue_handler = QueueHandler(log_queue)

logger = logging.getLogger('rotating_threaded_logger')
logger.setLevel(logging.DEBUG)

# Ротация логов, файлы до 10MB с максимумом в 5 копий
rotating_handler = RotatingFileHandler('app.log', maxBytes=10 * 1024 * 1024, backupCount=5)
rotating_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rotating_handler.setFormatter(formatter)

# Настройка консольного логирования
if os.getenv("LOG_TO_CONSOLE", "true").lower() == "true":
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

listener = QueueListener(log_queue, rotating_handler)
logger.addHandler(queue_handler)

def start_listener():
    listener.start()

def stop_listener():
    listener.stop()
