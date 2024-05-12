import uuid
import aiofiles

from typing import Sequence, Tuple

from fastapi import UploadFile

from config import FILE_DIR
from src.api.models import User, Tweet, Media
from src.api.schemas import (
    ResultBase,
    UserOut,
    ErrorBase,
    UserBase,
    FollowBase,
    TweetsOut,
    TweetBase,
    AuthorBase,
    LikeBase,
    TweetOut,
    MediaOut,
)


def build_create_media_response(media: Media) -> MediaOut:
    """
    Функция построения JSON-ответа файла
    :param media: Объект таблицы Media
    :return: JSON-ответ с результатом и id файла
    """
    response: MediaOut = MediaOut(
        result=True,
        media_id=media.id,
    )

    return response


def build_get_media_response(media: Media) -> Tuple[str, str]:
    """
    Функция построения пути и типа контента файла
    :param media: Объект таблицы Media
    :return: Кортеж из пути и типа контента файла
    """
    return f'{FILE_DIR}/{media.filename}', media.content_type


def build_create_tweet_response(tweet: Tweet) -> TweetOut:
    """
    Функция построения JSON-ответа для одного твита
    :param tweet: Объект таблицы Tweet
    :return: JSON-ответ с результатом и id твита
    """
    response: TweetOut = TweetOut(
        result=True,
        tweet_id=tweet.id,
    )

    return response


def build_get_tweets_response(tweets: Sequence[Tweet]) -> TweetsOut:
    """
    Функция построения JSON-ответа для всех твитов
    :param tweets: Последовательность твитов
    :return: JSON-ответ со ссылками на файлы, автором и лайками твита
    """
    response: TweetsOut = TweetsOut(
        result=True,
        tweets=[
            TweetBase(
                id=t.id,
                content=t.content,
                attachments=[f"/api/medias/{a.id}" for a in t.attachments],
                author=AuthorBase(id=t.author.id, name=t.author.name),
                likes=[LikeBase(user_id=like.user.id, name=like.user.name) for like in t.likes],
            )
            for t in tweets
        ],
    )

    return response


def build_error_response(error_type: str, error_message: str) -> ErrorBase:
    """
    Функция построения ошибочного JSON-ответа
    :param error_type: Тип ошибки
    :param error_message: Сообщение об ошибке
    :return: JSON-ответ с ошибкой
    """
    response: ErrorBase = ErrorBase(
        result=False,
        error_type=error_type,
        error_message=error_message,
    )

    return response


def build_result_response(result: bool) -> ResultBase:
    """
    Функция построения логического JSON-ответа
    :param result: Булево значение
    :return: JSON-ответ с результатом
    """
    response: ResultBase = ResultBase(
        result=result,
    )

    return response


def build_get_user_response(user: User) -> UserOut:
    """
    Функция построения JSON-ответа для получения юзера
    :param user: Объект таблицы User
    :return: JSON-ответ с подписчиками и подписками юзера
    """
    response: UserOut = UserOut(
        result=True,
        user=UserBase(
            id=user.id,
            name=user.name,
            followers=[
                FollowBase(id=follower.follower.id, name=follower.follower.name)
                for follower in user.followers
            ],
            following=[
                FollowBase(id=following.following.id, name=following.following.name)
                for following in user.following
            ],
        )
    )

    return response


async def upload_media(file: UploadFile) -> str:
    """
    Функция генерации уникального имени файла и сохранения файла на диск
    :param file: Загружаемый файл
    :return: Уникальное имя файла для последующего сохранения в базу данных
    """
    unique_filename: str = str(uuid.uuid4()) + "_" + file.filename

    async with aiofiles.open(f'{FILE_DIR}/{unique_filename}', mode='wb') as f:
        content: bytes = await file.read()
        await f.write(content)

    return unique_filename
