from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)

from config import (
    DB_USER,
    DB_PASS,
    DB_HOST,
    DB_PORT,
    DB_NAME,
)
from src.api.models import (
    Base,
    User,
    Tweet,
)

DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine: AsyncEngine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    """ Создание таблиц базы данных """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db_and_tables():
    """ Удаление таблиц базы данных """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """ Генератор асинхронной сессии """
    async with async_session() as session:
        yield session


async def create_db_data():
    """ Наполнение таблиц базы данных """
    async with async_session() as session:
        user1: User = User(api_key='test', name='Tony')
        user2: User = User(api_key='test2', name='Mike')
        user3: User = User(api_key='test3', name='John')
        session.add_all([user1, user2, user3])

        await session.commit()
        await session.refresh(user1)
        await session.refresh(user2)
        await session.refresh(user3)

        tweet1: Tweet = Tweet(content='First tweet', author_api_key='test')
        tweet2: Tweet = Tweet(content='Second tweet', author_api_key='test2')
        tweet3: Tweet = Tweet(content='Third tweet', author_api_key='test3')
        session.add_all([tweet1, tweet2, tweet3])

        await session.commit()

# async def create_test_db_data():
#     """ Наполнение таблиц базы данных для тестирования """
#     async with test_async_session() as session:
#         user1: User = User(api_key='test', name='Tony')
#         user2: User = User(api_key='test2', name='Mike')
#         session.add_all([user1, user2])
#
#         await session.commit()
#         await session.refresh(user1)
#         await session.refresh(user2)
#
#         user_follow1: Follower = Follower(follower_api_key='test', following_id=2)
#         user_follow2: Follower = Follower(follower_api_key='test2', following_id=1)
#         session.add_all([user_follow1, user_follow2])
#
#         await session.commit()
#         await session.refresh(user_follow1)
#         await session.refresh(user_follow2)
#
#         media1: Media = Media(filename='image1.png', content_type='image/png')
#         media2: Media = Media(filename='image2.png', content_type='image/png')
#         session.add_all([media1, media2])
#
#         await session.commit()
#         await session.refresh(media1)
#         await session.refresh(media2)
#
#         tweet1: Tweet = Tweet(content='First tweet', author_api_key='test')
#         tweet2: Tweet = Tweet(content='Second tweet', author_api_key='test2')
#         session.add_all([tweet1, tweet2])
#
#         await session.commit()
#         await session.refresh(tweet1)
#         await session.refresh(tweet2)
#
#         like1: TweetLike = TweetLike(user_api_key='test', tweet_id=1)
#         like2: TweetLike = TweetLike(user_api_key='test2', tweet_id=1)
#         session.add_all([like1, like2])
#
#         await session.commit()
