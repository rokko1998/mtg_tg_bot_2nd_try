import redis

# Инициализация клиента Redis
redis_client = redis.Redis(
    host='localhost',  # Адрес Redis-сервера
    port=6379,         # Порт Redis-сервера
    db=0,              # Используемая база данных Redis (по умолчанию)
    decode_responses=True  # Автоматическое декодирование ответов из байтов в строки
)