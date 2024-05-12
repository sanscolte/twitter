from typing import List

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship


class Base(AsyncAttrs, DeclarativeBase):
    """Базовая таблица с id"""

    id: Mapped[int] = mapped_column(
        primary_key=True,
        unique=True,
        autoincrement=True,
    )


class Media(Base):
    """Таблица для хранения имени и типа файла"""

    __tablename__ = "media"

    filename: Mapped[str]
    content_type: Mapped[str]

    tweet_id: Mapped[int] = mapped_column(
        ForeignKey("tweet.id", ondelete="CASCADE"),
        nullable=True,
    )
    tweet: Mapped["Tweet"] = relationship(
        lazy="joined",
        back_populates="attachments",
    )


class TweetLike(Base):
    """Таблица для хранения лайка на твит"""

    __tablename__ = "tweet_like"

    user_api_key: Mapped[str] = mapped_column(
        ForeignKey("user.api_key", ondelete="CASCADE"),
        nullable=False,
    )
    tweet_id: Mapped[int] = mapped_column(
        ForeignKey("tweet.id", ondelete="CASCADE"),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        lazy="joined",
        back_populates="liked_tweets",
        foreign_keys=[user_api_key],
    )
    tweet: Mapped["Tweet"] = relationship(
        lazy="joined",
        back_populates="likes",
        foreign_keys=[tweet_id],
    )

    __table_args__ = (
        UniqueConstraint(
            "user_api_key",
            "tweet_id",
            name="uq_user_api_key_tweet_id",
        ),
    )


class Tweet(Base):
    """Таблица для хранения твита"""

    __tablename__ = "tweet"

    content: Mapped[str]
    attachments: Mapped[List["Media"]] = relationship(
        back_populates="tweet",
    )

    author_api_key: Mapped[str] = mapped_column(ForeignKey("user.api_key"))
    author: Mapped["User"] = relationship(back_populates="tweets")

    likes: Mapped[List["TweetLike"]] = relationship(
        back_populates="tweet",
    )


class Follower(Base):
    """Таблица для хранения подписчиков, подписок"""

    __tablename__ = "follower"

    follower_api_key: Mapped[str] = mapped_column(
        ForeignKey("user.api_key"),
        nullable=False,
    )
    following_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        nullable=False,
    )

    follower: Mapped["User"] = relationship(
        lazy="joined",
        back_populates="followers",
        foreign_keys=[follower_api_key],
        overlaps="following",
    )
    following: Mapped["User"] = relationship(
        lazy="joined",
        back_populates="following",
        foreign_keys=[following_id],
        overlaps="following",
    )

    __table_args__ = (
        UniqueConstraint(
            "follower_api_key",
            "following_id",
            name="uq_follower_api_key_following_id",
        ),
    )


class User(Base):
    """Таблица для хранения пользователя"""

    __tablename__ = "user"

    api_key: Mapped[str] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str]
    tweets: Mapped[List["Tweet"]] = relationship(
        lazy="joined",
        back_populates="author",
        cascade="all, delete-orphan",
    )

    followers: Mapped[List["Follower"]] = relationship(
        lazy="joined",
        back_populates="follower",
        cascade="all, delete-orphan",
        foreign_keys=[Follower.following_id],
        overlaps="following",
    )
    following: Mapped[List["Follower"]] = relationship(
        lazy="joined",
        back_populates="following",
        cascade="all, delete-orphan",
        foreign_keys=[Follower.follower_api_key],
        overlaps="following",
    )
    liked_tweets: Mapped[List["TweetLike"]] = relationship(
        lazy="joined",
        back_populates="user",
        cascade="all, delete-orphan",
    )
