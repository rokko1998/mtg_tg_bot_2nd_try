from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import chat_action
# from state import FindGame,MyGames, Stats
from db.core import AsyncCore
from kb import start_kb

user_router = Router()

# Message хендлер команды старт, главное меню
@admin_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await AsyncCore.add_user(message.from_user.id, message.from_user.username, bot: Bot)
    await state.clear()
    #TODO
    # await router.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(text=f'Привет, {sts.username},\n'
                              f'Добро пожаловать в таверну "Гнутая мишень"!\n'
                              f'Здесь ты можешь записаться на драфт в МТГА\n\n'
                              f'Твоя статистика:\n'
                              f'Количество побед: {sts.wins}\n'
                              f'Винрейт: {winrate_text}',
                         reply_markup=start_kb)

# Хендлер кнопки "Найти игру" главного меню, выводит список турниров этой недели
@admin_router.callback_query(F.data == 'find_game')
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
@admin_router.callback_query(F.data == 'back_to_start')
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
