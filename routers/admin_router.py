from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import chat_action
# from state import FindGame,MyGames, Stats
from db.core import AsyncCore
from kb import start_kb
from logger_conf import logger
from state import Add_tnmt
from aiogram import Bot
import re

admin_router = Router()

# Регулярное выражение для проверки формата даты и времени ДД.ММ.ГГ ЧЧ.ММ
DATE_TIME_REGEX = r'^\d{2}\.\d{2}\.\d{2} \d{2}\.\d{2}$'


@admin_router.message(Command('add_tournament'))
async def cmd_add_tournament(message: Message, state: FSMContext):
    """Начало добавления нового турнира./Запрос даты"""
    # TODO Check_admin()
    await state.set_state(Add_tnmt.tnmt_date)
    await state.update_data(admin=True)
    await message.answer(text='Начнем создание нового турнира.\n'
                              'Для начала введите дату и время турнира в формате: ДД.ММ.ГГ ЧЧ.ММ')


@admin_router.message(Add_tnmt.tnmt_date)
async def set_tnmt_date(message: Message, state: FSMContext):
    """Хендлер Даты и времени проведения турнира./Запрос названия"""

    date_text = message.text
    # Проверяем соответствие формату даты и времени
    if not re.match(DATE_TIME_REGEX, date_text):
        # Если формат неправильный, отправляем сообщение об ошибке и просим повторить ввод
        await message.answer(text='Неверный формат даты и времени. Введите в формате: ДД.ММ.ГГ ЧЧ.ММ')
        return

    # Если формат правильный, продолжаем процесс
    await state.update_data(date=date_text)
    await state.set_state(Add_tnmt.tnmt_name)
    await message.answer(text=f'Турнир на {date_text}.\n'
                              'Теперь напишите название турнира')

@admin_router.message(Add_tnmt.tnmt_name)
async def add_tnmt(message: Message, state: FSMContext):
    """Хендлер названия турнира./Добавление в базу"""

    name = message.text
    date = (await state.get_data()).get("date")
    await AsyncCore.add_tournament(name, date)
    await message.answer(text='Турнир успешно создан!')
    await state.clear()


# @admin_router.callback_query(Add_tnmt.new_tnmt)
# async def set_tnmt_date(callback: CallbackQuery, state: FSMContext):
#     """Хендлер Даты и времени проведения турнира"""
#     await state.update_data(date=callback)
#     keyboard = InlineKeyboardBuilder()
#
#     for tournament in tournaments:
#         tournament_id = tournament.id
#         tournament_name = tournament.name
#         keyboard.button(
#             text=f'{tournament_name}',
#             callback_data=f'tournament_{tournament_id}'
#         )
#     keyboard.button(text='Назад', callback_data='back_to_start')
#
#     await callback.answer('Выберите турнир')
#     await callback.message.edit_text('Выберите турнир:', reply_markup=keyboard.adjust(2).as_markup())

