import sys
import os
import asyncio
import logging
from dotenv import load_dotenv
from os import getenv
from aiohttp import web
from redis.asyncio import Redis
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from aiogram.fsm.storage.redis import RedisStorage
from app.logger_conf import start_listener, stop_listener, logger
from app.mw import LogUserActionsMiddleware
from app.routers.user_router import user_router
from app.routers.admin_router import admin_router

# Загружаем переменные окружения
#load_dotenv()

# Получаем конфигурационные параметры
TOKEN = getenv('TOKEN')
OWNER_ID = getenv('OWNER_ID')
WEBHOOK_URL = getenv('WEBHOOK_URL', "https://mtgtgbot.online/webhook")
USE_POLLING = getenv('USE_POLLING', 'false').lower() == 'true'
REDIS_HOST = getenv('REDIS_HOST', 'redis')

# Проверка переменных окружения
if not TOKEN:
    raise ValueError("TOKEN не найден в переменных окружения!")
if not OWNER_ID:
    raise ValueError("OWNER_ID не найден в переменных окружения!")

# Подключение к Redis
redis = Redis(host=REDIS_HOST, port=6379, db=0)
storage = RedisStorage(redis=redis)

# Создаем экземпляр бота и диспетчера
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)
dp.message.middleware(LogUserActionsMiddleware())
dp.callback_query.middleware(LogUserActionsMiddleware())
dp.include_routers(user_router, admin_router)

async def delete_webhook_before_polling():
    """Удаляет вебхук перед запуском поллинга"""
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Webhook удален перед запуском поллинга.")
    except Exception as e:
        logging.error(f"Ошибка при удалении вебхука: {e}")

async def run_polling():
    """Запуск бота в режиме поллинга"""
    logging.info("Запуск бота в режиме поллинга")
    start_listener()
    try:
        await delete_webhook_before_polling()
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка при запуске поллинга: {e}")
    finally:
        stop_listener()
        logger.info("Слушатель логов остановлен.")

async def start_bot():
    """Устанавливаем вебхук и отправляем сообщение владельцу"""
    try:
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"Webhook успешно установлен на URL {WEBHOOK_URL}.")
    except Exception as e:
        logging.error(f"Ошибка при установке вебхука: {e}")
        raise
    await bot.send_message(chat_id=OWNER_ID, text='Бот запущен!')

async def handle(request):
    """Обрабатываем входящие обновления от Telegram через вебхук"""
    try:
        request_body_dict = await request.json()
        update = Update.to_object(request_body_dict)
        await dp.feed_update(bot, update)
        logging.info("Обновление обработано успешно")
    except Exception as e:
        logging.error(f"Ошибка при обработке обновления: {e}")
    return web.Response()

async def start_webhook():
    """Запускаем веб-сервер для приема вебхуков"""
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
        raise

async def main():
    """Основной запуск бота"""
    if USE_POLLING:
        await run_polling()
    else:
        await start_webhook()
        logging.info("Бот запущен!")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_listener()
    try:
        asyncio.run(main())  # Создаем единый event loop
    except KeyboardInterrupt:
        logger.warning("Бот был остановлен пользователем.")
    finally:
        stop_listener()
        logger.info("Слушатель логов остановлен.")
