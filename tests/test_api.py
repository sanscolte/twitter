from typing import Dict, Any

import pytest
from httpx import AsyncClient, Response


@pytest.mark.asyncio
async def test_create_medias(ac: AsyncClient) -> None:
    """ Тестирование создания файла по эндпоинту POST /api/medias """
    file_path: str = 'tests/test_files/test_image_1.png'

    with open(file_path, mode='rb') as file:
        response = await ac.post("/medias", files={"file": file})

    data: Dict[Any] = response.json()

    assert response.status_code == 201
    assert data['result'] is True
    assert 'media_id' in data


@pytest.mark.asyncio
async def test_get_medias(ac: AsyncClient) -> None:
    """ Тестирование получения файла по эндпоинту GET /api/medias """
    media_id: int = 1
    response: Response = await ac.get(f"/medias/{media_id}")

    assert response.status_code == 200
    assert response.headers['Content-Type'].startswith('image/')


@pytest.mark.asyncio
async def test_create_tweet(ac: AsyncClient) -> None:
    """ Тестирование создания твита по эндпоинту POST /api/tweets """
    json_data: Dict[str, str] = {
        "tweet_data": "New tweet",
        "tweet_media_ids": [1],
    }
    response: Response = await ac.post(
        '/tweets',
        json=json_data
    )
    data: Dict[Any] = response.json()

    assert response.status_code == 201
    assert data['result'] is True
    assert "tweet_id" in data


@pytest.mark.asyncio
async def test_like_tweet(ac: AsyncClient) -> None:
    """
    Тестирование добавления твита в понравившиеся
    по эндпоинту POST /api/tweets/{id}/likes
    """
    tweet_id: int = 1
    response: Response = await ac.post(f"/tweets/{tweet_id}/likes")
    data: Dict[Any] = response.json()

    assert response.status_code == 201
    assert data['result'] is True


@pytest.mark.asyncio
async def test_get_tweets(ac: AsyncClient) -> None:
    """ Тестирование получения всех твитов по эндпоинту GET /api/tweets """
    expected: Dict[Any] = {
        "result": True,
        "tweets": [
            {
                "id": 1,
                "content": "New tweet",
                "attachments": ['/api/medias/1'],
                "author": {"id": 1, "name": "Tony"},
                "likes": [{"user_id": 1, "name": "Tony"}],
            }
        ]
    }

    response: Response = await ac.get("/tweets")
    data: Dict[Any] = response.json()

    assert response.status_code == 200
    assert data == expected


@pytest.mark.asyncio
async def test_delete_like_tweet(ac: AsyncClient) -> None:
    """
    Тестирование удаления твита из понравившихся
    по эндпоинту DELETE /api/tweets/{id}/likes
    """
    tweet_id: int = 1
    response: Response = await ac.delete(f"/tweets/{tweet_id}/likes")
    data: Dict[Any] = response.json()

    assert response.status_code == 200
    assert data['result'] is True


@pytest.mark.asyncio
async def test_delete_tweet(ac: AsyncClient) -> None:
    """ Тестирование удаления твита по эндпоинту DELETE /api/tweets/{id} """
    tweet_id: int = 1
    response: Response = await ac.delete(f"/tweets/{tweet_id}")
    data = response.json()

    assert response.status_code == 200
    assert data['result'] is True


@pytest.mark.asyncio
async def test_follow_user(ac: AsyncClient) -> None:
    """ Тестирование подписки на юзера по эндпоинту POST /api/users/{id}/follow """
    user_id: int = 2
    response: Response = await ac.post(f"/users/{user_id}/follow")
    data: Dict[Any] = response.json()

    assert response.status_code == 201
    assert data['result'] is True


@pytest.mark.asyncio
async def test_get_user_me(ac: AsyncClient) -> None:
    """ Тестирование получения своего профиля по эндпоинту GET /api/users/me """
    expected: Dict[Any] = {
        "result": True,
        "user": {
            "id": 1,
            "name": "Tony",
            "followers": [],
            "following": [{"id": 2, "name": "Mike"}],
        }
    }

    response: Response = await ac.get("/users/me")
    data: Dict[Any] = response.json()

    assert response.status_code == 200
    assert data == expected


@pytest.mark.asyncio
async def test_get_user_by_id(ac: AsyncClient) -> None:
    """ Тестирование получения юзера по эндпоинту GET /api/users/{id} """
    user_id: int = 2
    expected: Dict[Any] = {
        "result": True,
        "user": {
            "id": 2,
            "name": "Mike",
            "followers": [{"id": 1, "name": "Tony"}],
            "following": [],
        }
    }

    response: Response = await ac.get(f"/users/{user_id}")
    data: Dict[Any] = response.json()

    assert response.status_code == 200
    assert data == expected


@pytest.mark.asyncio
async def test_unfollow_user(ac: AsyncClient) -> None:
    """ Тестирование отписки от юзера по эндпоинту DELETE /api/users/{id}/follow """
    user_id: int = 2
    response: Response = await ac.delete(f"/users/{user_id}/follow")
    data: Dict[Any] = response.json()

    assert response.status_code == 200
    assert data['result'] is True
