from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
import asyncio
import logging
import ssl
import ast
from dotenv import load_dotenv
from os import getenv
from logger_conf import start_listener, stop_listener, logger  # Импортируем listener и логгер
from mw import LogUserActionsMiddleware
from aiohttp import web
from redis.asyncio import Redis

from aiogram.types import Update  # Импортируем Update

from routers.user_router import user_router
from routers.admin_router import admin_router

# Создаем экземпляр Redis с указанием хоста, порта и базы данных
redis = Redis(host='localhost', port=6379, db=0)

# Настраиваем RedisStorage для работы с FSM
storage = RedisStorage(redis=redis)

load_dotenv()

TOKEN = getenv('TOKEN')
OWNER_ID = getenv('OWNER_ID')
WEBHOOK_URL = getenv('WEBHOOK_URL', "https://mtgtgbot.online/webhook")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)
dp.message.middleware(LogUserActionsMiddleware())
dp.callback_query.middleware(LogUserActionsMiddleware())

async def start_bot(bot: Bot):
    await bot.send_message(chat_id=OWNER_ID, text='Бот запущен!')
    await bot.set_webhook(WEBHOOK_URL)

# Определяем обработчик вебхука
async def handle(request):
    request_body_dict = await request.json()
    update = Update.to_object(request_body_dict)
    await dp.feed_update(bot, update)
    return web.Response()

# Настройка маршрута для вебхука и запуск веб-сервера
async def start_webhook():
    app = web.Application()
    app.router.add_post('/webhook', handle)  # Используем наш обработчик

    runner = web.AppRunner(app)
    await runner.setup()

    # Настройка SSL-контекста
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_context.load_cert_chain(
        '/etc/ssl/certs/fullchain.pem',
        '/etc/ssl/private/privkey.pem'
    )

    # Указание SSL-контекста при запуске веб-сервера
    site = web.TCPSite(runner, '0.0.0.0', 8443, ssl_context=ssl_context)  # Слушаем на порту 8443
    await site.start()
    logging.info("Веб-сервер успешно запущен и слушает вебхук.")

dp.startup.register(start_bot)
dp.include_routers(user_router, admin_router)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_listener()  # Запускаем слушателя очереди
    try:
        asyncio.run(start_webhook())
        logger.info("Бот запущен!")
    except KeyboardInterrupt:
        logger.warning(f"Бот был остановлен пользователем.\n\n\n")
    finally:
        stop_listener()  # Останавливаем слушателя очереди
        logger.info("Слушатель логов остановлен.")
