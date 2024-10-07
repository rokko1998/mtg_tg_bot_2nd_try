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
from state import Add_tnmt, Admin_panel
from aiogram import Bot
import re
from kb import admin_panel_kb

admin_router = Router()

# Регулярное выражение для проверки формата даты и времени ДД.ММ.ГГ ЧЧ.ММ
DATE_TIME_REGEX = r'^\d{2}\.\d{2}\.\d{2} \d{2}\.\d{2}$'

@admin_router.message(Command('admin_panel'))
async def admin_panel(message: Message, state: FSMContext):
    """Начало добавления нового турнира./Запрос даты"""
    # TODO Check_admin()
    await state.set_state(Admin_panel.ap_menu)
    await state.update_data(admin=True)
    await message.answer(text='Добро пожаловать на Кухню таверны "Гнутая мишень', reply_markup=admin_panel_kb)



@admin_router.callback_query(F.data == 'edit_tnmts')
async def cmd_add_tournament(callback: CallbackQuery, state: FSMContext):
    """Начало добавления нового турнира./Запрос даты"""
    # TODO Check_admin()
    await state.set_state(Add_tnmt.tnmt_date)
    await state.update_data(admin=True)
    await callback.message.edit_text(text='Начнем создание нового турнира.\n'
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
    await state.set_state(Add_tnmt.tnmt_set)
    await message.answer(text=f'Турнир на {date_text}.\n'
                              'Теперь напишите название турнира')

@admin_router.message(Add_tnmt.tnmt_set)
async def add_tnmt(message: Message, state: FSMContext):
    """Хендлер названия турнира.Запрос выбора сета"""

    name = message.text
    date = (await state.get_data()).get("date")
    await state.update_data(name=name)
    sets = await AsyncCore.get_sets()
    await state.set_state(Add_tnmt.tnmt_name)

    keyboard = InlineKeyboardBuilder()
    for set in sets:
        keyboard.button(text=set.name, callback_data=f'tnmt_set_{set.name}')
    keyboard.button(text='Голосование за сет', callback_data=f'vote')
    await message.answer('Выберите сет:', reply_markup=keyboard.adjust(3).as_markup())

@admin_router.callback_query(Add_tnmt.tnmt_name)
async def add_tnmt(callback: CallbackQuery, state: FSMContext):
    """Хендлер сета турнира./Добавление в базу"""
    name = (await state.get_data()).get("name")
    date = (await state.get_data()).get("date")
    tnmt = await AsyncCore.add_tournament(name, date)
    if callback.data != 'vote':
        set = callback.data.split("_")[-1]
        await AsyncCore.add_set(tnmt.id, set)
    await callback.message.edit_text('Турнир успешно создан!')
    await state.clear()



