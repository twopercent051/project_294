# import datetime
from datetime import datetime

from sqlalchemy import MetaData, inspect, Column, String, insert, select, Integer, TIMESTAMP, Text, update, delete, \
    DateTime, JSON
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker, as_declarative
from sqlalchemy.sql import expression

from create_bot import DATABASE_URL

engine = create_async_engine(DATABASE_URL)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@as_declarative()
class Base:
    metadata = MetaData()

    def _asdict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}


class UtcNow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(UtcNow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class UsersDB(Base):
    """Пользователи"""
    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(String, nullable=False)
    username = Column(String, nullable=True)


class TicketsDB(Base):
    """Обращения"""
    __tablename__ = "tickets"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    user_id = Column(String, nullable=False)
    username = Column(String, nullable=True)
    branch = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    phone_method = Column(String, nullable=True)
    level_1 = Column(String, nullable=True)
    level_2 = Column(String, nullable=False)
    petition = Column(Text, nullable=False)
    ticket_hash = Column(String, nullable=False)
    create_timestamp = Column(TIMESTAMP, nullable=False, server_default=UtcNow())
    media = Column(JSON, nullable=True)


class RemindsDB(Base):
    """Незавершённые тикеты"""
    __tablename__ = "reminds"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    ticket_hash = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    day = Column(Integer, nullable=False, server_default="0")


# class MediasDB(Base):
#     """Медиафайлы к обращениям"""
#     __tablename__ = 'medias'
#
#     id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
#     ticket_hash = Column(String, nullable=False)
#     type_obj = Column(String, nullable=False)
#     file_id = Column(String, nullable=False)


class TextsDB(Base):
    """Тексты сообщений бота"""
    __tablename__ = "texts"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    subject = Column(String, nullable=False)
    text = Column(Text, nullable=False)


class BaseDAO:
    """Класс взаимодействия с БД"""
    model = None

    @classmethod
    async def get_one_or_none(cls, **filter_by) -> dict:
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def get_many(cls, **filter_by) -> list:
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def create(cls, **data):
        async with async_session_maker() as session:
            stmt = insert(cls.model).values(**data)
            await session.execute(stmt)
            await session.commit()

    # @classmethod
    # async def update(cls, cond_dict: dict, **data):
    #     async with async_session_maker() as session:
    #         stmt = update(cls.model).where(cond_dict).values(**data)
    #         await session.execute(stmt)
    #         await session.commit()

    @classmethod
    async def delete(cls, **data):
        async with async_session_maker() as session:
            stmt = delete(cls.model).filter_by(**data)
            await session.execute(stmt)
            await session.commit()


class UserDAO(BaseDAO):
    model = UsersDB


class TextsDAO(BaseDAO):
    model = TextsDB

    @classmethod
    async def get_user_texts(cls, branch: str, chapter: str) -> list:
        key = f"branch:{branch}|chapter:{chapter}%"
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter(cls.model.subject.like(key))
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def update(cls, subject: str, **data):
        async with async_session_maker() as session:
            stmt = update(cls.model).filter_by(subject=subject).values(**data)
            await session.execute(stmt)
            await session.commit()


class RemindsDAO(BaseDAO):
    model = RemindsDB

    @classmethod
    async def update_reminds(cls):
        async with async_session_maker() as session:
            stmt = update(cls.model).values(day=cls.model.day + 1)
            await session.execute(stmt)
            await session.commit()


class TicketsDAO(BaseDAO):
    model = TicketsDB

    @classmethod
    async def get_users_by_branch(cls, branch: str) -> list:
        async with async_session_maker() as session:
            query = select(cls.model.user_id).filter_by(branch=branch).distinct()
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def get_db(cls, branch: str, period: datetime) -> list:
        async with async_session_maker() as session:
            if branch == "all":
                query = select(cls.model.__table__.columns).filter(cls.model.create_timestamp > period)
            else:
                query = select(cls.model.__table__.columns).filter(cls.model.create_timestamp > period).\
                    filter_by(branch=branch)
            result = await session.execute(query)
            return result.mappings().all()


# class MediasDAO(BaseDAO):
#     model = MediasDB

