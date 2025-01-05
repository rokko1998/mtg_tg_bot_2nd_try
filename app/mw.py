
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from logger_conf import logger

import inspect


class LogUserActionsMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject, data: Dict[str, Any]) -> Any:

        # Логируем входящее сообщение или колбэк-запрос
        if isinstance(event, Message):
            logger.info(f"Пользователь {event.from_user.id} отправил сообщение: {event.text}")
        elif isinstance(event, CallbackQuery):
            logger.info(f"Пользователь {event.from_user.id} отправил колбэк-запрос с данными: {event.data}")

        try:
            # Выполняем основной хендлер
            result = await handler(event, data)

            # Логируем факт отработки хендлера
            if isinstance(event, Message):
                logger.info(f"Хендлер  успешно отработал сообщение '{event.text}'")
            elif isinstance(event, CallbackQuery):
                logger.info(f"Хендлер успешно отработал колбэк '{event.data}'")

        except Exception as e:
            # Логируем ошибку если хендлер не смог обработать запрос
            if isinstance(event, Message):
                logger.warning(
                    f"Хендлер не смог отработать сообщение '{event.text}' от пользователя {event.from_user.id}: {e}")
            elif isinstance(event, CallbackQuery):
                logger.warning(
                    f"Хендлер не смог отработать колбэк-запрос '{event.data}' от пользователя {event.from_user.id}: {e}")
            raise e

        return result
