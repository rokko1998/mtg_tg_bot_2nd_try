from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio
import logging
import ast
from dotenv import load_dotenv
from os import getenv
from logger_conf import start_listener, stop_listener, logger  # Импортируем listener и логгер


from routers.user_router import user_router
from routers.admin_router import admin_router


load_dotenv()

TOKEN = getenv('TOKEN')
OWNER_ID = getenv('OWNER_ID')


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def start_bot(bot: Bot):
    await bot.send_message(chat_id=OWNER_ID, text='Бот запущен!')

dp.startup.register(start_bot)
dp.include_routers(user_router, admin_router)




async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_listener()  # Запускаем слушателя очереди
    try:
        asyncio.run(main())
        logger.info("Бот запущен!")
    except KeyboardInterrupt:
        logger.warning("Бот был остановлен пользователем.")
    finally:
        stop_listener()  # Останавливаем слушателя очереди
        logger.info("Слушатель логов остановлен.")
