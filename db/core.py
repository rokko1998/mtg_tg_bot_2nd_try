from typing import Optional
from typing import Dict
from sqlalchemy import select, case
from sqlalchemy.orm import selectinload, joinedload, outerjoin
from datetime import datetime, timedelta
from db.models import *
from sqlalchemy.exc import IntegrityError
from logger_conf import logger



class AsyncCore:
    @staticmethod
    async def add_user(tg_id: int, username: str) -> Optional[UserORM]:
        """Добавляет нового пользователя в базу данных."""
        async with async_session() as session:
            try:
                # Проверяем, существует ли пользователь
                new_user = UserORM(tg_id=tg_id, username=username)
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)  # Обновляем объект после коммита
                logger.info(f'Зарегистрирован новый пользователь {str(new_user)}')
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
            now = datetime.now()

            # Определяем начало и конец недели
            start_of_week = datetime.combine(now - timedelta(days=now.weekday()), datetime.min.time())
            end_of_week = datetime.combine(start_of_week + timedelta(days=6), datetime.max.time())

            # print(f"Start of week: {start_of_week}, End of week: {end_of_week}") # Вывод для отладки

            # Выполняем запрос на выборку турниров, которые начинаются на этой неделе
            result = await session.execute(
                select(TournamentORM)
                .where(TournamentORM.date >= start_of_week)
                .where(TournamentORM.date <= end_of_week)
            )

            tournaments = result.scalars().all()
            return tournaments

    @staticmethod
    async def get_start_stat(user_id: int) -> Dict[str, any]:
        """Возвращает данные пользователя, включая количество побед и винрейт."""
        async with async_session() as session:
            async with session.begin():
                # Запрос для получения данных пользователя и статистики матчей
                stmt = select(
                    UserORM.username,
                    func.sum(case(
                        (MatchORM.winner_id == UserORM.id, 1),
                        else_=0
                    )).label('wins'),
                    func.count().label('total_matches')
                ).outerjoin(
                    MatchORM, (MatchORM.player1_id == user_id) | (MatchORM.player2_id == user_id)
                ).where(UserORM.id == user_id).group_by(UserORM.username)

                result = await session.execute(stmt)
                data = result.fetchone()

                # Обработка результата
                if data:
                    username, wins, total_matches = data
                    return {
                        'username': username or 'Unknown',
                        'wins': wins or 0,
                        'total_matches': total_matches or 0
                    }
                else:
                    logger.warning(f'Ошибка при получении данных пользователя {user_id}')
                    return {
                        'username': 'Unknown',
                        'wins': 0,
                        'total_matches': 0
                    }

    @staticmethod
    async def add_tournament(name: str, date: str) -> Optional[TournamentORM]:
        """Добавляет новый турнир в базу данных."""
        async with async_session() as session:
            try:
                # Преобразуем строку даты в объект datetime
                tournament_date = datetime.strptime(date, "%d.%m.%y %H.%M")

                # Создаем новый объект турнира
                new_tournament = TournamentORM(
                    name=name,
                    date=tournament_date,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )

                session.add(new_tournament)
                await session.commit()
                await session.refresh(new_tournament)  # Обновляем объект после коммита
                logger.info(f'Создан новый турнир {str(new_tournament)}')
                return new_tournament
            except IntegrityError:
                # Откатываем транзакцию, если произошла ошибка
                await session.rollback()
                logger.error(f'Ошибка при добавлении турнира с именем {name}')
                return None