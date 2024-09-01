import datetime
import enum
import logging
import asyncio
from sqlalchemy import BigInteger, ForeignKey, func, String, Integer, DateTime, Enum, UniqueConstraint, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, Relationship, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from typing import Annotated, List

str_256 = Annotated[str, mapped_column(String(256))]
stat = Annotated[int, mapped_column(default=0)]
int_pk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime.datetime, mapped_column(server_default=func.now(), onupdate=func.now())]


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


class TournamentORM(Base):
    __tablename__ = 'tournaments'

    id: Mapped[int_pk]
    name: Mapped[str_256]
    status = mapped_column(Enum(TournamentStatus), default=TournamentStatus.PLANNED)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    registrations: Mapped[List["RegistrationORM"]] = Relationship(back_populates="tournament",
                                                                  cascade="all, delete-orphan")
    matches: Mapped[List["MatchORM"]] = Relationship(back_populates="tournament", cascade="all, delete-orphan")
    votes: Mapped[List["VoteORM"]] = Relationship(back_populates="tournament", cascade="all, delete-orphan")


class SetORM(Base):
    __tablename__ = 'sets'

    id: Mapped[int_pk]
    name: Mapped[str_256]
    release_date = mapped_column(DateTime)

    votes: Mapped[List["VoteORM"]] = Relationship(back_populates="set", cascade="all, delete-orphan")
    registrations: Mapped[List["RegistrationORM"]] = Relationship(back_populates="set", cascade="all, delete-orphan")


class RegistrationORM(Base):
    __tablename__ = 'registrations'

    id: Mapped[int_pk]
    user_id = mapped_column(ForeignKey('users.id'), nullable=False)
    tournament_id = mapped_column(ForeignKey('tournaments.id'), nullable=False)
    set_id = mapped_column(ForeignKey('sets.id'), nullable=False)
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
    __tablename__ = 'decks'

    id: Mapped[int_pk]
    user_id = mapped_column(ForeignKey('users.id'), nullable=False)
    tournament_id = mapped_column(ForeignKey('tournaments.id'), nullable=False)
    name: Mapped[str_256]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped["UserORM"] = Relationship(back_populates="decks")
    tournament: Mapped["TournamentORM"] = Relationship()

    __table_args__ = (
        UniqueConstraint('user_id', 'tournament_id', name='uq_user_tournament_deck'),
    )


class MTGAccountORM(Base):
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


async def main():
    pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO) # Подключение логирования
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')