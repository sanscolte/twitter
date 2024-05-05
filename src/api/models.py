from typing import List

from sqlalchemy import ForeignKey, Column, Integer, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship, backref


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class Tweet(Base):
    __tablename__ = 'tweet'

    content: Mapped[str]
    attachments: Mapped[List["Media"]] = []
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    author: Mapped["User"] = relationship(back_populates='tweets', lazy="selectin")
    likes: Mapped["User"] = relationship(
        secondary="tweet_like",
        back_populates='liked_tweets',
        # cascade='all, delete',
        lazy="selectin",
    )


class Media(Base):
    __tablename__ = 'media'

    file_path: Mapped[str]
    tweet_id: Mapped[int] = mapped_column(ForeignKey('tweet.id'))


class User(Base):
    __tablename__ = 'user'

    api_key: Mapped[str]
    name: Mapped[str]
    tweets: Mapped[List["Tweet"]] = relationship(back_populates="author", lazy="selectin")

    followers: Mapped[List["UserFollower"]] = relationship(
        "User",
        secondary="user_follower",
        primaryjoin="User.id==user_follower.c.following_id",
        secondaryjoin="User.id==user_follower.c.follower_id",
        backref=backref("following", lazy="selectin"),
        # cascade='all, delete',
        lazy='selectin',
    )

    liked_tweets: Mapped[List["TweetLike"]] = relationship(
        "Tweet",
        secondary="tweet_like",
        back_populates="likes",
        # cascade="all, delete",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User {self.name}> | {self.api_key} | Tweets {self.tweets} | Followers {self.followers} | Likes {self.liked_tweets}"


class UserFollower(Base):
    __tablename__ = 'user_follower'

    follower_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    following_id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='uq_follower_id_following_id'),
    )


class TweetLike(Base):
    __tablename__ = 'tweet_like'

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    tweet_id: Mapped[int] = mapped_column(ForeignKey('tweet.id'), primary_key=True)

    __table_args__ = (
        UniqueConstraint('tweet_id', 'user_id', name='uq_user_id_tweet_id'),
    )
