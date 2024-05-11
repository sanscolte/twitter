from typing import List

from pydantic import BaseModel


class ResultBase(BaseModel):
    """ Схема логического результата """
    result: bool


class ErrorBase(ResultBase):
    """ Схема ошибки. Родитель - ResultBase """
    error_type: str
    error_message: str


class MediaOut(ResultBase):
    """ Схема для результата загрузки файла. Родитель - ResultBase """
    media_id: int


class LikeBase(BaseModel):
    """ Схема лайка """
    user_id: int
    name: str


class AuthorBase(BaseModel):
    """ Схема автора """
    id: int
    name: str


class TweetBase(BaseModel):
    """ Схема твита """
    id: int
    content: str
    attachments: List[str] = []
    author: AuthorBase
    likes: List[LikeBase] = []


class TweetIn(BaseModel):
    """ Схема для создания твита """
    tweet_data: str
    tweet_media_ids: List[int] = []


class TweetOut(ResultBase):
    """ Схема для отдачи твита. Родитель - ResultBase """
    tweet_id: int


class TweetsOut(ResultBase):
    """ Схема для отдачи всех твитов. Родитель - ResultBase """
    tweets: List[TweetBase]


class FollowBase(AuthorBase):
    """ Схема фолловера. Родитель - AuthorBase """
    pass


class UserBase(AuthorBase):
    """ Схема юзера с подписчиками и подписками. Родитель - AuthorBase """
    followers: List[FollowBase] | None = []
    following: List[FollowBase] | None = []


class UserOut(ResultBase):
    """ Схема юзера. Родитель - ResultBase """
    user: UserBase
