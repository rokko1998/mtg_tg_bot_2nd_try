from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import chat_action
# from state import FindGame,MyGames, Stats
from db.core import AsyncCore
from kb import start_kb

admin_router = Router()

# Message хендлер команды старт, главное меню
@admin_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await AsyncCore.add_user(message.from_user.id, message.from_user.username)
    await state.clear()
    #TODO
    # await router.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(text=f'Привет, sts.username,\n'
                              f'Добро пожаловать в таверну "Гнутая мишень"!\n'
                              f'Здесь ты можешь записаться на драфт в МТГА\n\n'
                              f'Твоя статистика:\n'
                              f'Количество побед: sts.wins\n'
                              f'Винрейт: winrate_text',
                         reply_markup=start_kb)

# Хендлер кнопки "Назад" из меню "Найти игру" (выбора из списка турниров)
@admin_router.callback_query(F.data == 'back_to_start')
async def back_to_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    sts = await AsyncCore.get_user_sts(callback.from_user.id)

    total_games = sts.wins + sts.losses
    if total_games > 0:
        winrate = (sts.wins / total_games) * 100
        winrate_text = f"{winrate:.2f}%"
    else:
        winrate_text = "N/A"

    new_text = (f'Привет, {sts.username},\n'
                f'Добро пожаловать в таверну "Гнутая мишень"!\n'
                f'Здесь ты можешь записаться на драфт в МТГА\n\n'
                f'Твоя статистика:\n'
                f'Количество побед: {sts.wins}\n'
                f'Винрейт: {winrate_text}')

    await callback.message.edit_text(text=new_text, reply_markup=start_kb)
