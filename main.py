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
from logger_conf import start_listener, stop_listener, logger
from mw import LogUserActionsMiddleware
from aiohttp import web
from redis.asyncio import Redis
from aiogram.types import Update
from routers.user_router import user_router
from routers.admin_router import admin_router

# Подключение к Redis
redis = Redis(host='localhost', port=6379, db=0)
storage = RedisStorage(redis=redis)
load_dotenv()

# Получаем токен и настройки вебхука
TOKEN = getenv('TOKEN')
OWNER_ID = getenv('OWNER_ID')
WEBHOOK_URL = getenv('WEBHOOK_URL', "https://mtgtgbot.online/webhook")

# Создаем экземпляр бота и диспетчера
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)
dp.message.middleware(LogUserActionsMiddleware())
dp.callback_query.middleware(LogUserActionsMiddleware())

async def start_bot(bot: Bot):
    try:
        await bot.set_webhook(WEBHOOK_URL)
        logging.info("Webhook успешно установлен на URL %s.", WEBHOOK_URL)
    except Exception as e:
        logging.error(f"Ошибка при установке вебхука: {e}")
        raise  # Останавливаем запуск при ошибке установки вебхука
    await bot.send_message(chat_id=OWNER_ID, text='Бот запущен!')

async def handle(request):
    try:
        request_body_dict = await request.json()
        update = Update.to_object(request_body_dict)
        await dp.feed_update(bot, update)
        logging.info("Обновление обработано успешно")
    except Exception as e:
        logging.error(f"Ошибка при обработке обновления: {e}")
    return web.Response()

async def start_webhook():
    app = web.Application()
    app.router.add_post('/webhook', handle)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    try:
        await site.start()
        logging.info("Веб-сервер успешно запущен и слушает вебхук на порту 8080.")
    except Exception as e:
        logging.error(f"Ошибка при запуске веб-сервера: {e}")
        raise  # Остановим процесс при ошибке запуска

dp.startup.register(start_bot)
dp.include_routers(user_router, admin_router)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_listener()
    try:
        asyncio.run(start_webhook())
        logger.info("Бот запущен!")
    except KeyboardInterrupt:
        logger.warning("Бот был остановлен пользователем.")
    finally:
        stop_listener()
        logger.info("Слушатель логов остановлен.")
