from typing import Sequence, List

from fastapi import UploadFile
from sqlalchemy import (
    select,
    delete,
    Select,
    Result,
    Delete,
    CursorResult,
    desc,
    func,
)
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

    new_media: Media = Media(
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
    stmt: Select = select(Media).where(Media.id == media_id)

    result: Result = await session.execute(stmt)
    media: Media | None = result.scalar_one_or_none()

    return media


async def create_tweet_by_schema(
    session: AsyncSession,
    tweet: TweetIn,
    api_key: str | None,
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
        stmt: Select = select(Media).where(Media.id == media_id)
        result: Result = await session.execute(stmt)
        media: Media = result.scalars().one_or_none()  # type: ignore
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
    api_key: str | None,
) -> Sequence[Tweet] | None:
    """
    Функция получения всех твитов со ссылками на файлы, автором и лайками
    :param session: AsyncSession
    :return: Последовательность твитов
    """
    # Получение пользователей, на которых подписан текущий пользователь
    following_stmt: Select = (
        select(User)
        .join(Follower, Follower.follower_api_key == api_key)
        .filter(Follower.following_id == User.id)
    )
    following: Result = await session.execute(following_stmt)
    following: Result = following.unique()
    following_api_keys: List[str] = [user.api_key for user in following.scalars()]

    following_api_keys.append(api_key)  # type: ignore

    # Фильтрация твитов по пользователям
    tweets_query: Select = select(Tweet).filter(
        Tweet.author_api_key.in_(following_api_keys)
    )

    # Сортировка твитов по популярности (количеству лайков)
    sorted_tweets_query: Select = (
        tweets_query.options(selectinload(Tweet.attachments))
        .options(selectinload(Tweet.author))
        .options(selectinload(Tweet.likes))
        .join(TweetLike)
        .group_by(Tweet.id)
        .order_by(desc(func.count(TweetLike.tweet_id)))
    )

    tweet_result: Result = await session.execute(sorted_tweets_query)
    tweets: Sequence[Tweet] | None = tweet_result.scalars().all()

    return tweets


async def delete_tweet_by_id(
    session: AsyncSession,
    tweet_id: int,
    api_key: str | None,
) -> bool:
    """
    Функция удаления твита по id
    :param session: AsyncSession
    :param tweet_id: id твита
    :param api_key: api-key автора
    :return: Логический результат
    """
    stmt: Delete = delete(Tweet).where(
        (Tweet.id == tweet_id) & (Tweet.author_api_key == api_key),
    )

    result: CursorResult = await session.execute(stmt)
    if result.rowcount > 0:
        await session.commit()
        return True

    return False


async def like_by_tweet_id(
    session: AsyncSession,
    tweet_id: int,
    api_key: str | None,
) -> bool:
    """
    Функция добавления твита в понравившиеся по id
    :param session: AsyncSession
    :param tweet_id: id объекта Tweet
    :param api_key: api-key автора
    :return: Логический результат
    """
    try:
        new_like: TweetLike = TweetLike(
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
    api_key: str | None,
) -> bool:
    """
    Функция удаления твита из понравившихся по id
    :param session: AsyncSession
    :param tweet_id: id твита
    :param api_key: api-key автора
    :return: Логический результат
    """
    stmt: Delete = delete(TweetLike).where(
        (TweetLike.user_api_key == api_key) & (TweetLike.tweet_id == tweet_id),
    )

    result: CursorResult = await session.execute(stmt)
    if result.rowcount > 0:
        await session.commit()
        return True

    return False


async def get_user_by_api_key(
    session: AsyncSession,
    api_key: str | None,
) -> User | None:
    """
    Функция получения юзера по api-key
    :param session: AsyncSession
    :param api_key: api-key юзера
    :return: Объект таблицы User или None
    """
    stmt: Select = select(User).where(User.api_key == api_key)
    result: Result = await session.execute(stmt)
    result: Result = result.unique()
    user: User | None = result.scalar_one_or_none()

    return user


async def get_user_with_followers_and_following_by_api_key(
    session: AsyncSession,
    api_key: str | None,
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
    user_id: int | None,
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
    user_id: int | None,
) -> User | None:
    """
    Функция получения юзера по id
    :param session: AsyncSession
    :param user_id: id юзера
    :return: Объект таблицы User или None
    """
    stmt: Select = select(User).where(User.id == user_id)
    result: Result = await session.execute(stmt)
    result: Result = result.unique()
    user: User | None = result.scalar_one_or_none()

    return user


async def follow_by_user_id(
    session: AsyncSession,
    user_id: int,
    follower_api_key: str | None,
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
        new_follow = Follower(
            follower_api_key=follower_api_key, following_id=following.id
        )
        session.add(new_follow)
        await session.commit()
        return True

    return False


async def unfollow_by_user_id(
    session: AsyncSession,
    user_id: int,
    follower_api_key: str | None,
) -> bool:
    """
    Функция отписки от юзера по id
    :param session: AsyncSession
    :param user_id: id того, на кого подписывались
    :param follower_api_key: api-key подписчика
    :return: Логический результат
    """
    stmt: Delete = delete(Follower).where(
        (Follower.follower_api_key == follower_api_key)
        & (Follower.following_id == user_id),
    )

    result: CursorResult = await session.execute(stmt)
    if result.rowcount > 0:
        await session.commit()
        return True

    return False
