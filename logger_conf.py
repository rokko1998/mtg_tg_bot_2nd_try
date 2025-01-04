import logging
import queue
import os
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener

# Настройка очереди и логгера
log_queue = queue.Queue()
queue_handler = QueueHandler(log_queue)  # Использование QueueHandler для передачи логов в фоновом режиме, улучшая производительность и избегая блокировок.

logger = logging.getLogger('rotating_threaded_logger')
logger.setLevel(logging.DEBUG)

# Определение константы для максимального размера лог-файла
MAX_LOG_SIZE_MB = 10

# Директория для логов
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Убедимся, что директория логов существует
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Ротация логов, файлы до 10MB с максимумом в 5 копий
rotating_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_SIZE_MB * 1024 * 1024, backupCount=5)
rotating_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rotating_handler.setFormatter(formatter)

# Функция для проверки переменной окружения LOG_TO_CONSOLE
def should_log_to_console():
    return os.getenv("LOG_TO_CONSOLE", "true").lower() == "true"

# Настройка консольного логирования
if should_log_to_console():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

# Настройка слушателя для нескольких обработчиков
try:
    listener = QueueListener(log_queue, rotating_handler, *(logger.handlers))
    logger.addHandler(queue_handler)
except Exception as e:
    print(f"Ошибка при настройке логирования: {e}")

# Запуск слушателя
# Важно: Слушатель должен быть запущен до генерации любых лог-сообщений, чтобы все сообщения были обработаны корректно.
def start_listener():
    listener.start()

def stop_listener():
    listener.stop()
