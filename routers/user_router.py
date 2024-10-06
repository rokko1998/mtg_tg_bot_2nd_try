from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import chat_action
from db.core import AsyncCore
from aiogram import Bot
from kb import start_kb
from utils import generate_start_stat, handle_planned_tournament, handle_upcoming_tournament, handle_ongoing_tournament, \
    handle_completed_tournament, handle_cancelled_tournament
from logger_conf import logger
from state import Tnmts

user_router = Router()

@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    """Хендлер команды /start"""
    user = await AsyncCore.add_user(message.from_user.id, message.from_user.username)
    await state.clear()
    await state.set_state(Tnmts.start_menu)
    await state.update_data(user_id=str(user.id))
    sts = await AsyncCore.get_start_stat(user.id)
    msg = await generate_start_stat(sts)
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    # await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(text=msg, reply_markup=start_kb)


@user_router.callback_query(F.data == 'tnmts')
async def find_game(callback: CallbackQuery, state: FSMContext):
    """Хендлер кнопки "Турниры" главного меню, выводит список турниров этой недели"""
    tournaments = await AsyncCore.get_tournaments()
    await state.set_state(Tnmts.find_menu)
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

@user_router.callback_query(F.data.startswith('register_'))
@user_router.callback_query(F.data.startswith('change_set_'))
async def change_tournament_set(callback: CallbackQuery, state: FSMContext):
    tnmt_id = callback.data.split("_")[-1]
    await state.update_data(tnmt_id=str(tnmt_id))
    sets = await AsyncCore.get_sets()
    keyboard = InlineKeyboardBuilder()
    for set in sets:
        keyboard.button(text=set.name, callback_data=f'set_{set.id}')
    keyboard.button(text='назад', callback_data=f'Back_{set.id}')
    await callback.message.edit_text('Выберите сет:', reply_markup=keyboard.adjust(3).as_markup())


@user_router.callback_query(Tnmts.find_menu)
#@user_router.callback_query(F.data.startswith('tournament_'))
async def get_tournament_info(callback: CallbackQuery, state: FSMContext):
    """Хендлер трнира, выводит инфу по турниру и разные кнопки."""

    state_data = await state.get_data()
    user_id = int(state_data.get('user_id'))

    id = int(callback.data.split("_")[-1])
    prefix = callback.data.split("_")[0]
    if prefix == 'tournament':
        tnmt_id = id
        await state.update_data(tnmt_id=tnmt_id)

    state_data = await state.get_data()
    tnmt_id = int(state_data.get('tnmt_id'))

    if prefix == 'set':
        set = id
        register = await AsyncCore.reg_vote(tnmt_id, user_id, set)
        if register == True:
            await AsyncCore.register_user_to_tnmt(tnmt_id, user_id)

    if prefix == 'reg':
        await AsyncCore.register_user_to_tnmt(tnmt_id, user_id)

    if prefix == 'unregister':
        tnmt_id = int(state_data.get('tnmt_id'))
        await AsyncCore.unregister_user_to_tnmt(tnmt_id, user_id)


    # Получение данных о турнире и проверка регистрации пользователя
    tournament_data = await AsyncCore.get_tournament_data(tnmt_id)
    user_in_tournament = await AsyncCore.is_user_registered_in_tournament(tnmt_id, user_id)
    tournament_players = await AsyncCore.get_tournament_players(tnmt_id)
    set_votes = await AsyncCore.get_set_votes(tnmt_id)

    if not tournament_data:
        logger.error(f'Турнир не найден или данные недоступны.')
        await callback.message.edit_text("Турнир не найден или данные недоступны.")
        return


    # Вызов функции формирования сообщения и кнопок в зависимости от статуса турнира
    tournament_status = tournament_data['status']

    # Формирование сообщения и клавиатур в зависимости от статуса турнира и регистрации пользователя.
    if tournament_status == "planned":
        message_text, keyboard = await handle_planned_tournament(
            tournament_data, user_in_tournament, tournament_players, set_votes, user_id
        )
    elif tournament_status == "upcoming":
        message_text, keyboard = await handle_upcoming_tournament(
            tournament_data, user_in_tournament, tournament_players, user_id
        )
    elif tournament_status == "ongoing":
        message_text, keyboard = await handle_ongoing_tournament(
            tournament_data, user_in_tournament, tnmt_id, user_id
        )
    elif tournament_status == "completed":
        message_text, keyboard = await handle_completed_tournament(
            tournament_data, tournament_players
        )
    elif tournament_status == "cancelled":
        message_text, keyboard = await handle_cancelled_tournament(
            tournament_data
        )
    else:
        message_text = "Статус турнира не распознан. Пожалуйста, обратитесь к администратору."
        keyboard = InlineKeyboardBuilder().row(InlineKeyboardButton(text="Назад", callback_data="back")).as_markup()

    # Отправка или обновление сообщения с клавиатурой.
    await callback.message.edit_text(message_text, reply_markup=keyboard)



@user_router.callback_query(F.data.startswith('register_'))
async def tnmt_reg(callback: CallbackQuery, state: FSMContext):
    """Хендлер кнопки регистрации на турнир"""

