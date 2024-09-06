from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime, timedelta
from db.models import *


class AsyncCore:
    """Добавление пользователя"""
    @staticmethod
    async def add_user(tg_id: int, username: str) -> None:
        """Добавляет нового пользователя в базу данных."""
        async with async_session() as session:
            await session.execute(insert(UserORM).values(tg_id=tg_id, username=username).prefix_with("OR IGNORE"))
            await session.commit()

    @staticmethod
    async def create_tables():
        """Создание и заполнение временных таблиц"""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def add_test_data():
        """Основная функция для создания таблиц и добавления тестовых данных."""
        async with async_session() as session:
            Zontik_tournament = TournamentORM(name="Zontik", date=datetime(2024, 9, 10, 17, 30, 0))
            Brukwa_tournament = TournamentORM(name="Brukwa", date=datetime(2024, 9, 11, 17, 30, 0))
            El_tournament = TournamentORM(name="El", date=datetime(2024, 9, 11, 17, 30, 0))
            set_dominaria = SetORM(name='Dominaria')
            set_phirexya = SetORM(name='Phirexya')
            set_eldraine = SetORM(name='Eldraine')

            await session.add_all(
                [Zontik_tournament, Brukwa_tournament, El_tournament, set_phirexya, set_dominaria, set_eldraine])
            await session.commit()

