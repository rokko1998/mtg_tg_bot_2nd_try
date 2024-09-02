from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime, timedelta
from db.models import *
from dotenv import load_dotenv
from os import getenv

load_dotenv()
DB_USER = getenv('DB_USER')
DB_PASS = getenv('DB_PASS')
DB_HOST = getenv('DB_HOST')
DB_NAME = getenv('DB_NAME')


engine = create_async_engine(url='postgresql://tg_bot_db.sqlite3', echo=True)
async_session = async_sessionmaker(engine)

class AsyncCore:
    @staticmethod
    async def create_tables():
        """Создает все таблицы в базе данных."""
        async with engine.begin() as conn:
            # await conn.run_sync(Base.metadata.drop_all) удаляет все таблицы
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def add_user(tg_id: BigInteger, username: str):
        """Добавляет нового пользователя в базу данных."""
        async with async_session() as session:
            await session.execute(insert(UserORM).values(tg_id=tg_id, username=username).prefix_with("OR IGNORE"))
            await session.commit()

