from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton


start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Турниры', callback_data='tnmts'),
     InlineKeyboardButton(text='Статистика', callback_data='my_games')],
    [InlineKeyboardButton(text='Настройки', callback_data='statistics')]
])

admin_panel_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Управление турнирами', callback_data='edit_tnmts'),
     InlineKeyboardButton(text='Статистика', callback_data='my_games')],
    [InlineKeyboardButton(text='Настройки', callback_data='statistics')]
])