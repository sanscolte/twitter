from typing import Sequence, List

from fastapi import UploadFile
from sqlalchemy import select, delete, Select, Result, Delete, CursorResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.models import User, Tweet, TweetLike, Follower, Media
from src.api.schemas import TweetIn
from src.api.utils import upload_media


async def create_media(
        session: AsyncSession,
        file: UploadFile,
) -> Media | None:
    """
    Функция создания объекта Media
    :param session: AsyncSession
    :param file: Загружаемый файл
    :return: Media или None
    """
    unique_filename: str = await upload_media(file)

    new_media: Media | None = Media(
        filename=unique_filename,
        content_type=file.content_type,
    )
    session.add(new_media)
    await session.commit()

    return new_media


async def get_media(
        session: AsyncSession,
        media_id: int,
) -> Media | None:
    """
    Функция для получения объекта Media по id
    :param session: AsyncSession
    :param media_id: id файла
    :return: Media или None
    """
    stmt: Select = (
        select(Media)
        .where(Media.id == media_id)
    )

    result: Result = await session.execute(stmt)
    media: Media | None = result.scalar_one_or_none()

    return media


async def create_tweet_by_schema(
        session: AsyncSession,
        tweet: TweetIn,
        api_key: str,
) -> Tweet | None:
    """
    Функция создания твита по схеме
    :param session: AsyncSession
    :param tweet: Входная схема твита
    :param api_key: api-key автора
    :return: Объект таблицы Tweet или None
    """
    attachments: List[Media] = []
    for media_id in tweet.tweet_media_ids:
        stmt: Select = (
            select(Media)
            .where(Media.id == media_id)
        )
        result: Result = await session.execute(stmt)
        media: Media | None = result.scalars().one_or_none()
        attachments.append(media)

    new_tweet: Tweet = Tweet(
        content=tweet.tweet_data,
        author_api_key=api_key,
        attachments=attachments,
    )
    session.add(new_tweet)
    await session.commit()

    return new_tweet


async def get_all_tweets(
        session: AsyncSession,
) -> Sequence[Tweet] | None:
    """
    Функция получения всех твитов со ссылками на файлы, автором и лайками
    :param session: AsyncSession
    :return: Последовательность твитов
    """
    stmt: Select = (
        select(Tweet)
        .options(selectinload(Tweet.attachments))
        .options(selectinload(Tweet.author))
        .options(selectinload(Tweet.likes))
    )

    result: Result = await session.execute(stmt)
    tweets: Sequence[Tweet] | None = result.scalars().all()

    return tweets


async def delete_tweet_by_id(
        session: AsyncSession,
        tweet_id: int,
        api_key: str,
) -> bool:
    """
    Функция удаления твита по id
    :param session: AsyncSession
    :param tweet_id: id твита
    :param api_key: api-key автора
    :return: Логический результат
    """
    stmt: Delete = (
        delete(Tweet).where(
            (Tweet.id == tweet_id) &
            (Tweet.author_api_key == api_key),
        )
    )

    result: CursorResult = await session.execute(stmt)
    if result.rowcount > 0:
        await session.commit()
        return True

    return False


async def like_by_tweet_id(
        session: AsyncSession,
        tweet_id: int,
        api_key: str,
) -> bool:
    """
    Функция добавления твита в понравившиеся по id
    :param session: AsyncSession
    :param tweet_id: id объекта Tweet
    :param api_key: api-key автора
    :return: Логический результат
    """
    try:
        new_like: Tweet | None = TweetLike(
            user_api_key=api_key,
            tweet_id=tweet_id,
        )
        session.add(new_like)
        await session.commit()
        return True

    except IntegrityError:
        return False


async def delete_like_by_tweet_id(
        session: AsyncSession,
        tweet_id: int,
        api_key: str,
) -> bool:
    """
    Функция удаления твита из понравившихся по id
    :param session: AsyncSession
    :param tweet_id: id твита
    :param api_key: api-key автора
    :return: Логический результат
    """
    stmt: Delete = (
        delete(TweetLike).where(
            (TweetLike.user_api_key == api_key) &
            (TweetLike.tweet_id == tweet_id),
        )
    )

    result: CursorResult = await session.execute(stmt)
    if result.rowcount > 0:
        await session.commit()
        return True

    return False


async def get_user_by_api_key(
        session: AsyncSession,
        api_key: str,
) -> User | None:
    """
    Функция получения юзера по api-key
    :param session: AsyncSession
    :param api_key: api-key юзера
    :return: Объект таблицы User или None
    """
    stmt: Select = (
        select(User)
        .where(User.api_key == api_key)
    )
    result: Result = await session.execute(stmt)
    result: Result = result.unique()
    user: User | None = result.scalar_one_or_none()

    return user


async def get_user_with_followers_and_following_by_api_key(
        session: AsyncSession,
        api_key: str,
) -> User | None:
    """
    Функция получения юзера с подписчиками и подписками по api-key
    :param session: AsyncSession
    :param api_key: api-key юзера
    :return: Объект таблицы User или None
    """
    stmt: Select = (
        select(User)
        .options(selectinload(User.followers))
        .options(selectinload(User.following))
        .where(User.api_key == api_key)
    )
    result: Result = await session.execute(stmt)
    result: Result = result.unique()
    user: User | None = result.scalar_one_or_none()

    return user


async def get_user_with_followers_and_following_by_id(
        session: AsyncSession,
        user_id: int,
) -> User | None:
    """
     Функция получения юзера с подписчиками и подписками по id
    :param session: AsyncSession
    :param user_id: id юзера
    :return: Объект таблицы User или None
    """
    stmt: Select = (
        select(User)
        .options(selectinload(User.followers))
        .options(selectinload(User.following))
        .where(User.id == user_id)
    )
    result: Result = await session.execute(stmt)
    result: Result = result.unique()
    user: User | None = result.scalar_one_or_none()

    return user


async def get_user_by_id(
        session: AsyncSession,
        user_id: int,
) -> User | None:
    """
    Функция получения юзера по id
    :param session: AsyncSession
    :param user_id: id юзера
    :return: Объект таблицы User или None
    """
    stmt: Select = (
        select(User)
        .where(User.id == user_id)
    )
    result: Result = await session.execute(stmt)
    result: Result = result.unique()
    user: User | None = result.scalar_one_or_none()

    return user


async def follow_by_user_id(
        session: AsyncSession,
        user_id: int,
        follower_api_key: str,
) -> bool:
    """
    Функция подписки на юзера по id
    :param session: AsyncSession
    :param user_id: id того, на кого подписываемся
    :param follower_api_key: api-key подписчика
    :return: Логический результат
    """
    following: User | None = await get_user_by_id(session, user_id)

    if following:
        new_follow = Follower(follower_api_key=follower_api_key, following_id=following.id)
        session.add(new_follow)
        await session.commit()
        return True

    return False


async def unfollow_by_user_id(
        session: AsyncSession,
        user_id: int,
        follower_api_key: str,
) -> bool:
    """
    Функция отписки от юзера по id
    :param session: AsyncSession
    :param user_id: id того, на кого подписывались
    :param follower_api_key: api-key подписчика
    :return: Логический результат
    """
    stmt: Delete = (
        delete(Follower).where(
            (Follower.follower_api_key == follower_api_key) &
            (Follower.following_id == user_id),
        )
    )

    result: CursorResult = await session.execute(stmt)
    if result.rowcount > 0:
        await session.commit()
        return True

    return False
