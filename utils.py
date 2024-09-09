from typing import Dict

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
