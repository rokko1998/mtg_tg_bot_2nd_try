from datetime import datetime
import enum
import asyncio
from sqlalchemy import BigInteger, ForeignKey, func, String, Integer, DateTime, Enum, UniqueConstraint, Index, insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Relationship, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from typing import Annotated, List

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from dotenv import load_dotenv
from os import getenv

load_dotenv()

DB_USER = getenv('DB_USER')
DB_PASS = getenv('DB_PASS')
DB_HOST = getenv('DB_HOST')
DB_PORT = getenv('DB_PORT', '5432')  # По умолчанию порт 5432
DB_NAME = getenv('DB_NAME')
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine)




str_256 = Annotated[str, mapped_column(String(256))]
stat = Annotated[int, mapped_column(default=0)]
int_pk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=func.now())]


class TournamentStatus(enum.Enum):
    PLANNED = "planned"
    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RegStatus(enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Base(AsyncAttrs, DeclarativeBase):
    pass


class UserORM(Base):
    """Таблица пользователей"""
    __tablename__ = 'users'

    id: Mapped[int_pk]
    tg_id = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str_256]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    registrations: Mapped[List["RegistrationORM"]] = Relationship(back_populates="user", cascade="all, delete-orphan")
    decks: Mapped[List["DeckORM"]] = Relationship(back_populates="user", cascade="all, delete-orphan")
    mtg_accounts: Mapped[List["MTGAccountORM"]] = Relationship(back_populates="user", cascade="all, delete-orphan")
    votes: Mapped[List["VoteORM"]] = Relationship(back_populates="user", cascade="all, delete-orphan")
    def __str__(self):
        return f'username= {self.username}\ntg_id= {self.tg_id}'

class TournamentORM(Base):
    """Таблица турниров"""
    __tablename__ = 'tournaments'

    id: Mapped[int_pk]
    name: Mapped[str_256]
    status = mapped_column(Enum(TournamentStatus), default=TournamentStatus.PLANNED)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    date: Mapped[datetime]

    registrations: Mapped[List["RegistrationORM"]] = Relationship(back_populates="tournament",
                                                                  cascade="all, delete-orphan")
    matches: Mapped[List["MatchORM"]] = Relationship(back_populates="tournament", cascade="all, delete-orphan")
    votes: Mapped[List["VoteORM"]] = Relationship(back_populates="tournament", cascade="all, delete-orphan")

    def __str__(self):
        return f'id= {self.id}\ndate= {self.date}'


class SetORM(Base):
    """Таблица сетов"""
    __tablename__ = 'sets'

    id: Mapped[int_pk]
    name: Mapped[str_256]

    votes: Mapped[List["VoteORM"]] = Relationship(back_populates="set", cascade="all, delete-orphan")
    registrations: Mapped[List["RegistrationORM"]] = Relationship(back_populates="set", cascade="all, delete-orphan")

    def __str__(self):
        return self.name

class RegistrationORM(Base):
    """Таблица записей о регистрации пользователей в турнирах"""
    __tablename__ = 'registrations'

    id: Mapped[int_pk]
    user_id = mapped_column(ForeignKey('users.id'), nullable=False)
    tournament_id = mapped_column(ForeignKey('tournaments.id'), nullable=False)
    set_id = mapped_column(ForeignKey('sets.id'))
    status = mapped_column(Enum(RegStatus), default=RegStatus.CONFIRMED)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped["UserORM"] = Relationship(back_populates="registrations")
    tournament: Mapped["TournamentORM"] = Relationship(back_populates="registrations")
    set: Mapped["SetORM"] = Relationship(back_populates="registrations")

    __table_args__ = (
        UniqueConstraint('user_id', 'tournament_id', name='uq_user_tournament'),
    )


class DeckORM(Base):
    """Таблица с колодами пользователей"""
    __tablename__ = 'decks'

    id: Mapped[int_pk]
    user_id = mapped_column(ForeignKey('users.id'), nullable=False)
    tournament_id = mapped_column(ForeignKey('tournaments.id'), nullable=False)
    # name: Mapped[str_256]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped["UserORM"] = Relationship(back_populates="decks")
    tournament: Mapped["TournamentORM"] = Relationship()

    __table_args__ = (
        UniqueConstraint('user_id', 'tournament_id', name='uq_user_tournament_deck'),
    )


class MTGAccountORM(Base):
    """Таблица с аккаунтами MTG Arena пользователей"""
    __tablename__ = 'mtg_accounts'

    id: Mapped[int_pk]
    user_id = mapped_column(ForeignKey('users.id'), nullable=False)
    tournament_id = mapped_column(ForeignKey('tournaments.id'), nullable=False)
    account_name: Mapped[str_256]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped["UserORM"] = Relationship(back_populates="mtg_accounts")
    tournament: Mapped["TournamentORM"] = Relationship()

    __table_args__ = (
        UniqueConstraint('user_id', 'tournament_id', name='uq_user_tournament_account'),
    )


class VoteORM(Base):
    """Таблица с голосами пользователей за сет в рамках турниров"""
    __tablename__ = 'votes'

    id: Mapped[int_pk]
    user_id = mapped_column(ForeignKey('users.id'), nullable=False)
    tournament_id = mapped_column(ForeignKey('tournaments.id'), nullable=False)
    set_id = mapped_column(ForeignKey('sets.id'), nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped["UserORM"] = Relationship(back_populates="votes")
    tournament: Mapped["TournamentORM"] = Relationship(back_populates="votes")
    set: Mapped["SetORM"] = Relationship(back_populates="votes")

    __table_args__ = (
        UniqueConstraint('user_id', 'tournament_id', name='uq_user_tournament_vote'),
    )


class MatchORM(Base):
    """Таблица с результатами матчей"""
    __tablename__ = 'matches'

    id: Mapped[int_pk]
    tournament_id = mapped_column(ForeignKey('tournaments.id'), nullable=False)
    round = mapped_column(Integer, nullable=False)
    player1_id = mapped_column(ForeignKey('users.id'), nullable=False)
    player2_id = mapped_column(ForeignKey('users.id'), nullable=False)
    player1_score = mapped_column(Integer, default=0)
    player2_score = mapped_column(Integer, default=0)
    winner_id = mapped_column(ForeignKey('users.id'), nullable=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    tournament: Mapped["TournamentORM"] = Relationship(back_populates="matches")
    player1: Mapped["UserORM"] = Relationship(foreign_keys=[player1_id])
    player2: Mapped["UserORM"] = Relationship(foreign_keys=[player2_id])
    winner: Mapped["UserORM"] = Relationship(foreign_keys=[winner_id])

    __table_args__ = (
        UniqueConstraint('tournament_id', 'round', 'player1_id', 'player2_id', name='uq_match'),
        Index('ix_tournament_round', 'tournament_id', 'round')
    )


async def create_and_populate_db():
    """Создание всех таблиц и добавление тестовых данных"""
    async with engine.begin() as conn:
        # Использование run_sync для создания таблиц
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        async with session.begin():
            # Вставка тестовых данных в таблицу sets
            sets = [
                SetORM(name="Zendikar Rising"),
                SetORM(name="Kaldheim"),
                SetORM(name="Strixhaven: School of Mages")
            ]

            # Вставка тестовых данных в таблицу tournaments
            tournaments = [
                TournamentORM(name="Zendikar Championship", date=datetime(2024, 12, 5)),
                TournamentORM(name="Kaldheim Open", date=datetime(2024, 11, 20))
            ]

            # Добавление данных в сессию
            session.add_all(sets)
            session.add_all(tournaments)

        await session.commit()
        print(f'\033[92m Таблицы созданы и тестовые данные добавлены. \033[0m')

if __name__ == "__main__":
    asyncio.run(create_and_populate_db())


