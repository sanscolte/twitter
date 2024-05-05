import asyncio
from typing import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
from src.api.models import Base, User, UserFollower, Tweet, TweetLike

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


if __name__ == '__main__':
    async def create_db():
        async with async_session() as conn:
            user1 = User(api_key='test1', name='Tony', tweets=[], followers=[], liked_tweets=[])
            user2 = User(api_key='test2', name='Mike', tweets=[], followers=[], liked_tweets=[])
            user3 = User(api_key='test3', name='John', tweets=[], followers=[], liked_tweets=[])
            conn.add_all([user1, user2, user3])

            await conn.commit()
            await conn.refresh(user1)
            await conn.refresh(user2)

            user_follow1 = UserFollower(follower_id=1, following_id=2)
            user_follow2 = UserFollower(follower_id=2, following_id=1)
            user_follow3 = UserFollower(follower_id=2, following_id=3)
            conn.add_all([user_follow1, user_follow2, user_follow3])

            await conn.commit()
            await conn.refresh(user_follow1)
            await conn.refresh(user_follow2)

            tweet1 = Tweet(content='First tweet', author_id=1)
            tweet2 = Tweet(content='Second tweet', author_id=2)
            tweet3 = Tweet(content='Third tweet', author_id=2)
            conn.add_all([tweet1, tweet2, tweet3])

            await conn.commit()
            await conn.refresh(tweet1)
            await conn.refresh(tweet2)

            like1 = TweetLike(tweet_id=1, user_id=1)
            like2 = TweetLike(tweet_id=1, user_id=2)
            like3 = TweetLike(tweet_id=2, user_id=1)
            like4 = TweetLike(tweet_id=2, user_id=2)
            conn.add_all([like1, like2, like3, like4])

            await conn.commit()


    async def select_user():
        async with async_session() as conn:
            result = await conn.execute(
                select(User)
                .options(selectinload(User.tweets))
                .options(selectinload(User.liked_tweets))
                .options(selectinload(User.followers))
                .where(User.api_key == 'test1')
            )

            user = result.scalar_one()

            print(user)


    asyncio.run(drop_db_and_tables())
    asyncio.run(create_db_and_tables())
    asyncio.run(create_db())
    asyncio.run(select_user())
