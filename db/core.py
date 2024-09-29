from typing import Optional
from sqlalchemy import func
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
                user = existing_user.scalar_one()
                logger.info(f'Пользователь {str(user)} авторизован')
                return user

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

    @staticmethod
    async def get_tournament_data(tournament_id: int) -> Optional[dict]:
        """Получает информацию о турнире по его ID."""
        async with async_session() as session:
            result = await session.execute(
                select(TournamentORM)
                .where(TournamentORM.id == tournament_id)
                .options(selectinload(TournamentORM.registrations), selectinload(TournamentORM.votes))
            )
            tournament = result.scalar_one_or_none()
            if not tournament:
                return None

            return {
                'id': tournament.id,
                'name': tournament.name,
                'status': tournament.status.value,
                'date': tournament.date,
                'set': tournament.set,
                'players': len(tournament.registrations)  # Количество игроков
            }

    @staticmethod
    async def is_user_registered_in_tournament(tournament_id: int, user_id: int) -> bool:
        """Проверяет, зарегистрирован ли пользователь в турнире."""
        async with async_session() as session:
            result = await session.execute(
                select(RegistrationORM)
                .where(RegistrationORM.tournament_id == tournament_id)
                .where(RegistrationORM.user_id == user_id)
                .where(RegistrationORM.status == RegStatus.CONFIRMED)
            )
            return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_tournament_players(tournament_id: int) -> List[dict]:
        """Получает список всех зарегистрированных игроков для конкретного турнира."""
        async with async_session() as session:
            result = await session.execute(
                select(UserORM.id, UserORM.username, DeckORM.id.label('deck_id'))
                .join(RegistrationORM, RegistrationORM.user_id == UserORM.id)
                .outerjoin(DeckORM, (DeckORM.user_id == UserORM.id) & (DeckORM.tournament_id == tournament_id))
                .where(RegistrationORM.tournament_id == tournament_id)
                .where(RegistrationORM.status == RegStatus.CONFIRMED)
                .order_by(UserORM.username)
            )

            players = result.all()
            return [{'user_id': player.id, 'username': player.username, 'deck': player.deck_id is not None} for player
                    in players]

    @staticmethod
    async def get_set_votes(tournament_id: int) -> List[dict]:
        """Получает информацию о количестве голосов за каждый сет для конкретного турнира."""
        async with async_session() as session:
            result = await session.execute(
                select(SetORM.name, func.count(VoteORM.id).label('votes'))
                .join(VoteORM, VoteORM.set_id == SetORM.id)
                .where(VoteORM.tournament_id == tournament_id)
                .group_by(SetORM.name)
                .order_by(func.count(VoteORM.id).desc())
            )

            sets = result.all()
            return [{'name': set_data.name, 'votes': set_data.votes} for set_data in sets]

    @staticmethod
    async def get_tournament_matches(tournament_id: int) -> List[dict]:
        """Получает список всех матчей для конкретного турнира, сгруппированных по раундам."""
        async with async_session() as session:
            result = await session.execute(
                select(
                    MatchORM.round,
                    UserORM.username.label('player1'),
                    UserORM.username.label('player2'),
                    MatchORM.player1_score,
                    MatchORM.player2_score,
                    func.coalesce(UserORM.username, 'N/A').label('winner')
                )
                .join(UserORM, UserORM.id == MatchORM.player1_id)
                .join(UserORM, UserORM.id == MatchORM.player2_id)
                .join(UserORM, UserORM.id == MatchORM.winner_id, isouter=True)
                .where(MatchORM.tournament_id == tournament_id)
                .order_by(MatchORM.round)
            )

            matches = result.all()
            return [
                {
                    'round': match.round,
                    'player1': match.player1,
                    'player2': match.player2,
                    'player1_score': match.player1_score,
                    'player2_score': match.player2_score,
                    'winner': match.winner
                }
                for match in matches
            ]

    @staticmethod
    async def get_tournament_results(tournament_id: int) -> List[dict]:
        """Получает итоговую таблицу результатов для завершенного турнира."""
        async with async_session() as session:
            result = await session.execute(
                select(UserORM.username, func.rank().over(order_by=func.count(MatchORM.id)).label('position'))
                .join(RegistrationORM, RegistrationORM.user_id == UserORM.id)
                .join(MatchORM, (MatchORM.player1_id == UserORM.id) | (MatchORM.player2_id == UserORM.id))
                .where(RegistrationORM.tournament_id == tournament_id)
                .group_by(UserORM.username)
                .order_by(func.count(MatchORM.id).desc())
            )

            results = result.all()
            return [{'username': res.username, 'position': res.position} for res in results]