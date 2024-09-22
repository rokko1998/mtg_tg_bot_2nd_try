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
from utils import generate_start_stat
from logger_conf import logger
from state import FindGame

user_router = Router()

@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    """Хендлер команды /start"""
    user = await AsyncCore.add_user(message.from_user.id, message.from_user.username)
    # logger.info(f'Пользователь {str(user)} ввел команду старт')
    await state.clear()
    await state.set_state(FindGame.find_menu)
    await state.update_data(user_id=str(user.id))
    sts = await AsyncCore.get_start_stat(user.id)
    # logger.info(f'Пользователь {str(user)} ввел команду старт')
    msg = await generate_start_stat(sts)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(text=msg, reply_markup=start_kb)

@user_router.callback_query(F.data == 'find_game')
async def find_game(callback: CallbackQuery, state: FSMContext):
    """Хендлер кнопки "Найти игру" главного меню, выводит список турниров этой недели"""
    tournaments = await AsyncCore.get_tournaments()
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
    await callback.message.edit_text('Выберите турнир:', reply_markup=keyboard.adjust(2).as_markup())

#
# # Хендлер кнопки "Назад" из меню "Найти игру" (выбора из списка турниров)
# @user_router.callback_query(F.data == 'back_to_start')
# async def back_to_start(callback: CallbackQuery, state: FSMContext):
#     await state.clear()
#
#     sts = await AsyncCore.get_user_sts(callback.from_user.id)
#     # print(f"\033[92m {sts} - ok \033[0m")
#     # print(f"\033[92m AsyncCore.get_user_sts (F.data == back_to_start) - ok \033[0m")
#
#     total_games = sts.wins + sts.losses
#     if total_games > 0:
#         winrate = (sts.wins / total_games) * 100
#         winrate_text = f"{winrate:.2f}%"
#     else:
#         winrate_text = "N/A"
#
#     new_text = (f'Привет, {sts.username},\n'
#                 f'Добро пожаловать в таверну "Гнутая мишень"!\n'
#                 f'Здесь ты можешь записаться на драфт в МТГА\n\n'
#                 f'Твоя статистика:\n'
#                 f'Количество побед: {sts.wins}\n'
#                 f'Винрейт: {winrate_text}')
#
#     await callback.message.edit_text(text=new_text, reply_markup=start_kb)
