from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio
import logging
import ast
from dotenv import load_dotenv
import os

#rethb123


load_dotenv()

token = os.getenv('TOKEN')
OWNER_ID = os.getenv('ADMIN_ID')

bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def start_bot(bot: Bot):
    await bot.send_message(chat_id=OWNER_ID, text='Бот запущен!')

dp.startup.register(start_bot)


async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO) # Подключение логирования
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
