from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime, timedelta
from db.models import *
from sqlalchemy.exc import IntegrityError

class AsyncCore:
    from sqlalchemy.exc import IntegrityError

    @staticmethod
    async def add_user(tg_id: int, username: str) -> UserORM:
        """Добавляет нового пользователя в базу данных."""
        async with async_session() as session:
            try:
                # Проверяем, существует ли пользователь
                new_user = UserORM(tg_id=tg_id, username=username)
                session.add(new_user)
                await session.commit()
                return new_user
            except IntegrityError:
                # Откатываем транзакцию, если пользователь уже существует
                await session.rollback()

                # Возвращаем существующего пользователя
                existing_user = await session.execute(
                    select(UserORM).where(UserORM.tg_id == tg_id)
                )
                return existing_user.scalar_one()


    @staticmethod
    async def get_tournaments() -> List:
        """Возвращает список всех турниров, которые проходят на этой неделе"""
        async with async_session() as session:
            # Получаем текущую дату и время
            now = datetime.now()

            # Определяем начало и конец текущей недели
            start_of_week = now - timedelta(days=now.weekday())
            end_of_week = start_of_week + timedelta(days=6)

            # Выполняем запрос на выборку турниров, которые начинаются на этой неделе
            result = await session.execute(
                select(TournamentORM)
                .where(TournamentORM.date >= start_of_week)
                .where(TournamentORM.date <= end_of_week)
            )

            tournaments = result.scalars().all()
            return tournaments


    @staticmethod
    async def create_tables():
        """Создание и заполнение временных таблиц"""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


