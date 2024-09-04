from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import chat_action
# from state import FindGame,MyGames, Stats
from db.core import AsyncCore
from aiogram import Bot
from kb import start_kb
from utils import *

user_router = Router()

@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    """Хендлер команды /start"""
    await AsyncCore.add_user(message.from_user.id, message.from_user.username)
    await state.clear()
    #TODO sts = AsyncCore.get_main_stat(message.from_user.id) -> Dict
    # msg = generate_main_stat(sts: Dict) -> str
    msg = (f'Привет, sts.username,\n'
           f'Добро пожаловать в таверну "Гнутая мишень"!\n'
           f'Здесь ты можешь записаться на драфт в МТГА\n\n'
           f'Твоя статистика:\n'
           f'Количество побед: sts.wins\n'
           f'Винрейт: winrate_text')
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(text=msg, reply_markup=start_kb)

# Хендлер кнопки "Найти игру" главного меню, выводит список турниров этой недели
@user_router.callback_query(F.data == 'find_game')
async def find_game(callback: CallbackQuery, state: FSMContext):
    dates = await nearest_weekend()
    # print(f"\033[92m{dates}\033[0m")
    tournaments = await AsyncCore.upsert_tournaments(dates)
    print(f"\033[92m AsyncCore.upsert_tournaments - ok \033[0m")
    keyboard = InlineKeyboardBuilder()

    for tournament in tournaments:
        tournament_id = tournament.id
        tournament_name = tournament.name
        keyboard.button(
            text=f'{tournament_name}',
            callback_data=f'tournament_{tournament_id}'
        )
    keyboard.button(text='Назад', callback_data='back_to_start')

    await callback.answer('Выберите турнир')
    await state.set_state(FindGame.find_menu)
    await callback.message.edit_text('Выберите турнир:', reply_markup=keyboard.adjust(2).as_markup())


# Хендлер кнопки "Назад" из меню "Найти игру" (выбора из списка турниров)
@user_router.callback_query(F.data == 'back_to_start')
async def back_to_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    sts = await AsyncCore.get_user_sts(callback.from_user.id)
    # print(f"\033[92m {sts} - ok \033[0m")
    # print(f"\033[92m AsyncCore.get_user_sts (F.data == back_to_start) - ok \033[0m")

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
