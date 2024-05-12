from typing import Sequence, Annotated

from fastapi import APIRouter, Depends, Request, HTTPException, Path, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from src.api.models import User, Tweet, Media
from src.api.schemas import (
    UserOut,
    ResultBase,
    TweetsOut,
    TweetOut,
    TweetIn,
    MediaOut,
    ErrorBase,
)
from src.api.service import (
    get_user_with_followers_and_following_by_api_key,
    delete_tweet_by_id,
    get_all_tweets,
    like_by_tweet_id,
    delete_like_by_tweet_id,
    follow_by_user_id,
    unfollow_by_user_id,
    get_user_with_followers_and_following_by_id,
    create_tweet_by_schema,
    create_media,
    get_media,
)
from src.api.utils import (
    build_get_user_response,
    build_result_response,
    build_get_tweets_response,
    build_create_tweet_response,
    build_error_response,
    build_create_media_response,
    build_get_media_response,
)

router: APIRouter = APIRouter(
    prefix="/api",
    tags=["API"],
)


@router.post("/medias", response_model=MediaOut, status_code=201)
async def create_medias(
    file: UploadFile,
    session: AsyncSession = Depends(get_async_session),
) -> MediaOut:
    """
    Эндпоинт для загрузки файла
    :param file: Загружаемый файл
    :param session: AsyncSession
    :return: Схема MediaOut
    """
    if file.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(
            status_code=400,
            detail="Media validation failed",
        )

    new_media: Media | None = await create_media(session, file)

    if new_media is None:
        raise HTTPException(
            status_code=400,
            detail="Media validation failed",
        )

    response: MediaOut = build_create_media_response(new_media)
    return response


@router.get("/medias/{media_id}", response_model=None, status_code=200)
async def get_medias(
    media_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> FileResponse:
    """
    Эндпоинт для получения файла по id
    :param media_id: id файла
    :param session: AsyncSession
    :return: Файл
    """
    media: Media | None = await get_media(session, media_id)

    if not media:
        raise HTTPException(
            status_code=404,
            detail="Media not found",
        )

    file_path, content_type = build_get_media_response(media)
    response: FileResponse = FileResponse(file_path, media_type=content_type)
    return response


@router.post("/tweets", response_model=TweetOut, status_code=201)
async def create_tweet(
    request: Request,
    tweet: TweetIn,
    session: AsyncSession = Depends(get_async_session),
) -> TweetOut:
    """
    Эндпоинт
    :param request: Запрос
    :param tweet: Схема TweetIn
    :param session: AsyncSession
    :return: Схема TweetOut
    """
    api_key: str | None = request.headers.get("api-key")
    new_tweet: Tweet | None = await create_tweet_by_schema(
        session,
        tweet,
        api_key,
    )

    if not new_tweet:
        raise HTTPException(
            status_code=400,
            detail="Tweet validation failed",
        )

    response: TweetOut = build_create_tweet_response(tweet=new_tweet)
    return response


@router.get("/tweets", response_model=TweetsOut | ErrorBase, status_code=200)
async def get_tweets(
    session: AsyncSession = Depends(get_async_session),
) -> TweetsOut | ErrorBase:
    """
    Эндпоинт для получения всех твитов
    :param session: AsyncSession
    :return: Схема TweetsOut или ErrorBase
    """
    tweets: Sequence[Tweet] | None = await get_all_tweets(session)

    if not tweets:
        error_response: ErrorBase = build_error_response(
            "404",
            "There are no tweets yet",
        )
        return error_response

    response: TweetsOut = build_get_tweets_response(tweets)
    return response


@router.delete("/tweets/{id}", response_model=ResultBase, status_code=200)
async def delete_tweet(
    request: Request,
    tweet_id: Annotated[int, Path(alias="id")],
    session: AsyncSession = Depends(get_async_session),
) -> ResultBase:
    """
    Эндпоинт для удаления твита по id
    :param request: Запрос
    :param tweet_id: id твита
    :param session: AsyncSession
    :return: Схема ResultBase
    """
    api_key: str | None = request.headers.get("api-key")
    check_tweet_deleted: bool = await delete_tweet_by_id(
        session,
        tweet_id,
        api_key,
    )

    if not check_tweet_deleted:
        raise HTTPException(
            status_code=404,
            detail="Tweet you can delete not found",
        )

    response: ResultBase = build_result_response(True)
    return response


@router.post("/tweets/{id}/likes", response_model=ResultBase, status_code=201)
async def like_tweet(
    request: Request,
    tweet_id: Annotated[int, Path(alias="id")],
    session: AsyncSession = Depends(get_async_session),
) -> ResultBase:
    """
    Эндпоинт для добавления твита в понравившиеся
    :param request: Запрос
    :param tweet_id: id твита
    :param session: AsyncSession
    :return: Схема ResultBase
    """
    api_key: str | None = request.headers.get("api-key")
    check_tweet_like: bool = await like_by_tweet_id(session, tweet_id, api_key)

    if not check_tweet_like:
        raise HTTPException(
            status_code=404,
            detail="Tweet you can like not found",
        )

    response: ResultBase = build_result_response(True)
    return response


@router.delete("/tweets/{id}/likes", response_model=ResultBase, status_code=200)
async def delete_like_tweet(
    request: Request,
    tweet_id: Annotated[int, Path(alias="id")],
    session: AsyncSession = Depends(get_async_session),
) -> ResultBase:
    """
    Эндпоинт для удаления твита из понравившихся
    :param request: Запрос
    :param tweet_id: id твита
    :param session: AsyncSession
    :return: Схема ResultBase
    """
    api_key: str | None = request.headers.get("api-key")
    check_tweet_like: bool = await delete_like_by_tweet_id(
        session,
        tweet_id,
        api_key,
    )

    if not check_tweet_like:
        raise HTTPException(
            status_code=404,
            detail="Tweet's like not found",
        )

    response: ResultBase = build_result_response(True)
    return response


@router.get("/users/me", response_model=UserOut, status_code=200)
async def get_user_me(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> UserOut:
    """
    Эндпоинт для получения своего профиля
    :param request: Запрос
    :param session: AsyncSession
    :return: Схема UserOut
    """
    api_key: str | None = request.headers.get("api-key")
    user: User | None = await get_user_with_followers_and_following_by_api_key(
        session,
        api_key,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    response: UserOut = build_get_user_response(user)
    return response


@router.get("/users/{id}", response_model=UserOut, status_code=200)
async def get_user_by_id(
    user_id: Annotated[int, Path(alias="id")],
    session: AsyncSession = Depends(get_async_session),
) -> UserOut:
    """
    Эндпоинт для получения юзера по id
    :param user_id: id юзера
    :param session: AsyncSession
    :return: Схема UserOut
    """
    user: User | None = await get_user_with_followers_and_following_by_id(
        session,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    response: UserOut = build_get_user_response(user)
    return response


@router.post("/users/{id}/follow", response_model=ResultBase, status_code=201)
async def follow_user(
    request: Request,
    user_id: Annotated[int, Path(alias="id")],
    session: AsyncSession = Depends(get_async_session),
) -> ResultBase:
    """
    Эндпоинт для подписки на юзера по id
    :param request: Запрос
    :param user_id: id того, на кого подписываемся
    :param session: AsyncSession
    :return: Схема ResultBase
    """
    api_key: str | None = request.headers.get("api-key")
    check_follow: bool = await follow_by_user_id(session, user_id, api_key)

    if not check_follow:
        raise HTTPException(
            status_code=404,
            detail="User you can subscribe not found",
        )

    response: ResultBase = build_result_response(True)
    return response


@router.delete("/users/{id}/follow", response_model=ResultBase, status_code=200)
async def unfollow_user(
    request: Request,
    user_id: Annotated[int, Path(alias="id")],
    session: AsyncSession = Depends(get_async_session),
) -> ResultBase:
    """
    Эндпоинт для отписки от юзера по id
    :param request: Запрос
    :param user_id: id того, на кого подписывались
    :param session: AsyncSession
    :return: Схема ResultBase
    """
    api_key: str | None = request.headers.get("api-key")
    check_follow: bool = await unfollow_by_user_id(session, user_id, api_key)

    if not check_follow:
        raise HTTPException(
            status_code=404,
            detail="You were not subscribed to this user",
        )

    response: ResultBase = build_result_response(True)
    return response
