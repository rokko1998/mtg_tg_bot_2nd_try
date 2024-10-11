from typing import Dict, List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.core import AsyncCore


async def generate_start_stat(sts: Dict[str, any]) -> str:
    """Возвращает текст для сообщения со статистикой пользователя для команды старт"""
    username = sts.get('username', 'пользователь')
    wins = sts.get('wins', 0)
    losses = sts.get('losses', 0)

    total_games = wins + losses
    if total_games > 0:
        winrate = (wins / total_games * 100)
        winrate_text = f"{winrate:.2f}%"
    else:
        winrate_text = "не определен"

    message = (
        f"Привет, {username},\n"
        f"Добро пожаловать в таверну \"Гнутая мишень\"!\n"
        f"Здесь ты можешь записаться на драфт в МТГА\n\n"
        f"Твоя статистика:\n"
        f"Количество побед: {wins}\n"
        f"Винрейт: {winrate_text}\n"
    )
    return message

async def handle_planned_tournament(
    tournament_data: dict,
    user_in_tournament: bool,
    tournament_players: List[dict],
    set_votes: List[dict],
    user_id: int
) -> tuple[str, InlineKeyboardMarkup]:
    """
    Формирует сообщение и клавиатуру для турнира в статусе PLANNED.

    :param tournament_data: Данные о турнире.
    :param user_in_tournament: Указывает, зарегистрирован ли пользователь в турнире.
    :param tournament_players: Список всех зарегистрированных игроков турнира.
    :param set_votes: Список голосов за сет.
    :param user_id: ID текущего пользователя.
    :return: Сообщение и клавиатура для отправки пользователю.
    """
    # Формирование сообщения о турнире с использованием HTML-разметки
    message = f"<b>{tournament_data['name']}</b>\n" \
              f"<b>Статус турнира:</b> {tournament_data['status']} мск\n" \
              f"<b>Дата проведения:</b> {tournament_data['date'].strftime('%d.%m %H:%M')}\n" \
              f"<b>Кол-во игроков:</b> {len(tournament_players)}\n\n"

    set_exists = bool(tournament_data.get('set'))

    if set_exists:
        message += f"<b>Сет турнира:</b> {tournament_data['set']}\n"


    if len(tournament_players) != 0:
        # Список игроков
        message += "<b>Список всех игроков данного турнира:</b>\n"

        # Формируем список пользователей, текущий пользователь выводится первым, а остальные - в порядке очереди.
        if user_in_tournament:
            # Добавляем текущего пользователя в начало списка.
            for player in tournament_players:
                if player['user_id'] == user_id:
                    player_text = f"<b>{player['username']}</b>"  # Выделение текущего пользователя жирным.
                    message += f"{player_text}\n"
                    break  # Прекращаем цикл после добавления пользователя

        # Добавляем остальных игроков, пропуская текущего пользователя.
        for player in tournament_players:
            if player['user_id'] != user_id:  # Пропускаем текущего пользователя.
                player_text = f"{player['username']}"
                message += f"{player_text}\n"

        if not set_exists:
            # Голосование за сет
            message += "\nГолосование за сет:\n"
            set_votes_sorted = sorted(set_votes, key=lambda x: x['votes'], reverse=True)[:3]  # Топ-3 сета
            for set_info in set_votes_sorted:
                message += f"{set_info['name']} - {set_info['votes']} голосов\n"



    # Создание клавиатуры
    keyboard = InlineKeyboardBuilder()

    if user_in_tournament:
        # Если пользователь уже зарегистрирован, добавляем кнопку "Отменить регистрацию"
        keyboard.row(
            InlineKeyboardButton(text="Отменить регистрацию", callback_data=f"unregister_{tournament_data['id']}")
        )

        # Если сет отсутствует, добавляем кнопку "Выбор сета"
        if not set_exists:
            keyboard.row(
                InlineKeyboardButton(text="Выбор сета", callback_data=f"change_set_{tournament_data['id']}")
            )
    else:
        # Если пользователь не зарегистрирован, добавляем кнопку "Зарегистрироваться" с измененным callback_data, если сет уже есть
        callback_data = f"reg_{tournament_data['id']}" if set_exists else f"register_{tournament_data['id']}"
        keyboard.add(
            InlineKeyboardButton(text="Зарегистрироваться", callback_data=callback_data)
        )

    # Добавление кнопок, которые отображаются всегда
    keyboard.row(
        InlineKeyboardButton(text="Обновить", callback_data=f"refresh_{tournament_data['id']}"),
        InlineKeyboardButton(text="Назад", callback_data="back")
    )

    return message, keyboard.as_markup()

async def handle_upcoming_tournament(
    tournament_data: dict,

    user_in_tournament: bool,
    tournament_players: List[dict],
    user_id: int
) -> tuple[str, InlineKeyboardMarkup]:
    """
    Формирует сообщение и клавиатуру для турнира в статусе UPCOMING.

    :param tournament_data: Данные о турнире.
    :param user_in_tournament: Указывает, зарегистрирован ли пользователь в турнире.
    :param tournament_players: Список всех зарегистрированных игроков турнира.
    :param user_id: ID текущего пользователя.
    :return: Сообщение и клавиатура для отправки пользователю.
    """
    # Формирование сообщения о турнире с использованием HTML-разметки
    message = f"<b>{tournament_data['name']}</b>\n" \
              f"<b>Статус турнира:</b> {tournament_data['status']}\n" \
              f"<b>Сет:</b> {tournament_data['set']}\n\n"

    # Список игроков
    message += "<b>Список всех игроков данного турнира:</b>\n"
    for index, player in enumerate(tournament_players, start=1):
        player_status = "Указана колода" if player['deck'] else "Колода не указана"
        player_text = f"{index}. {player['username']} - {player_status}"
        if user_in_tournament and player['user_id'] == user_id:
            player_text = f"<b>{player_text}</b>"  # Выделение текущего пользователя жирным.
        message += f"{player_text}\n"


    # Создание клавиатуры
    keyboard = InlineKeyboardBuilder()

    # Добавление кнопок в зависимости от состояния колоды игрока
    if user_in_tournament:
        if not player['deck']:
            keyboard.add(InlineKeyboardButton(text="Зарегистрировать колоду",
                                              callback_data=f"register_deck_{tournament_data['id']}"))
        else:
            keyboard.add(
                InlineKeyboardButton(text="Изменить колоду", callback_data=f"change_deck_{tournament_data['id']}"))

    # Добавление кнопок, которые отображаются всегда
    keyboard.row(
        InlineKeyboardButton(text="Обновить", callback_data=f"refresh_{tournament_data['id']}"),
        InlineKeyboardButton(text="Назад", callback_data="back")
    )

    # Возвращение сообщения и клавиатуры в формате InlineKeyboardMarkup
    return message, keyboard.as_markup()


async def handle_ongoing_tournament(
        tournament_data: dict,
        user_in_tournament: bool,
        tournament_id: int,
        user_id: int
) -> tuple[str, InlineKeyboardMarkup]:
    """
    Формирует сообщение и клавиатуру для турнира в статусе ONGOING.

    :param tournament_data: Данные о турнире.
    :param user_in_tournament: Указывает, зарегистрирован ли пользователь в турнире.
    :param tournament_id: ID текущего турнира.
    :param user_id: ID текущего пользователя.
    :return: Сообщение и клавиатура для отправки пользователю.
    """
    # Получение текущих матчей турнира
    matches = await AsyncCore.get_tournament_matches(tournament_id)

    # Формирование сообщения о турнире с использованием HTML-разметки
    message = f"<b>{tournament_data['name']}</b>\n" \
              f"> Статус турнира: {tournament_data['status']}\n" \
              f"Сет: {tournament_data['set']}\n\n"

    message += "Текущие матчи:\n"
    for match in matches:
        message += f"{match['player1']} VS {match['player2']} - результат матча: {match['player1_score']} : {match['player2_score']}\n"


    # Создание клавиатуры
    keyboard = InlineKeyboardBuilder()

    # Добавление кнопок в клавиатуру
    keyboard.row(
        InlineKeyboardButton(text="Внести результаты матча", callback_data=f"enter_results_{tournament_id}"),
        InlineKeyboardButton(text="Обновить", callback_data=f"refresh_{tournament_id}")
    )
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="back"))

    return message, keyboard.as_markup()


async def handle_completed_tournament(
        tournament_data: dict,
        tournament_players: List[dict]
) -> tuple[str, InlineKeyboardMarkup]:
    """
    Формирует сообщение и клавиатуру для турнира в статусе COMPLETED.

    :param tournament_data: Данные о турнире.
    :param tournament_players: Список всех игроков турнира.
    :return: Сообщение и клавиатура для отправки пользователю.
    """
    message = f"<b>{tournament_data['name']}</b>\n"
    message += f"> Статус турнира: {tournament_data['status']}\n"
    message += f"Сет: {tournament_data['set']}\n"

    message += "Таблица результатов:\n"
    for index, player in enumerate(tournament_players, start=1):
        message += f"{index}. {player['username']}\n"

    # Клавиатура
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="back"))

    return message, keyboard.as_markup()

async def handle_cancelled_tournament(
    tournament_data: dict
) -> tuple[str, InlineKeyboardMarkup]:
    """
    Формирует сообщение и клавиатуру для турнира в статусе CANCELLED.

    :param tournament_data: Данные о турнире.
    :return: Сообщение и клавиатура для отправки пользователю.
    """
    message = f"<b>{tournament_data['name']}</b>\n"
    message += f"> Статус турнира: {tournament_data['status']}\n"

    # Клавиатура
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="back"))

    return message, keyboard.as_markup()
