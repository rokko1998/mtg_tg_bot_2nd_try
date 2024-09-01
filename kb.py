from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton


start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Найти игру', callback_data='find_game'),
     InlineKeyboardButton(text='Мои игры', callback_data='my_games')],
    [InlineKeyboardButton(text='Статистика', callback_data='statistics')]
])