from typing import List

from sqlalchemy import ForeignKey, UniqueConstraint, LargeBinary
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class Media(Base):
    __tablename__ = 'media'

    file_body: Mapped[bytes] = mapped_column(LargeBinary)
    file_name: Mapped[str]
    tweet_id: Mapped[int] = mapped_column(ForeignKey('tweet.id'), nullable=False)
    tweet: Mapped['Tweet'] = relationship(lazy='joined', back_populates='attachments')


class TweetLike(Base):
    __tablename__ = 'tweet_like'

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    tweet_id: Mapped[int] = mapped_column(ForeignKey('tweet.id'), nullable=False)

    user: Mapped["User"] = relationship(
        lazy='joined',
        back_populates='liked_tweets',
        foreign_keys=[user_id]
    )
    tweet: Mapped["Tweet"] = relationship(
        lazy='joined',
        back_populates='likes',
        foreign_keys=[tweet_id]
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'tweet_id', name='uq_user_id_tweet_id'),
    )


class Tweet(Base):
    __tablename__ = 'tweet'

    content: Mapped[str]
    attachments: Mapped[List["Media"]] = relationship(
        lazy='joined',
        back_populates='tweet',
        cascade='all, delete-orphan',
    )

    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    author: Mapped["User"] = relationship(lazy='joined', back_populates='tweets')

    likes: Mapped[List["TweetLike"]] = relationship(
        lazy='joined',
        back_populates='tweet',
        cascade='all, delete-orphan',
    )


class Follower(Base):
    __tablename__ = 'follower'

    follower_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    following_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    follower: Mapped['User'] = relationship(
        lazy='joined',
        back_populates='followers',
        foreign_keys=[follower_id],
    )
    following: Mapped['User'] = relationship(
        lazy='joined',
        back_populates='following',
        foreign_keys=[following_id],
    )

    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='uq_follower_id_following_id'),
    )

    def to_json_followers(self):
        return {
            'id': self.follower.id,
            'name': self.follower.name,
        }

    def to_json_following(self):
        return {
            'id': self.following.id,
            'name': self.following.name,
        }


class User(Base):
    __tablename__ = 'user'

    api_key: Mapped[str]
    name: Mapped[str]
    tweets: Mapped[List["Tweet"]] = relationship(lazy='joined', back_populates="author")

    followers: Mapped[List["Follower"]] = relationship(
        lazy='joined',
        back_populates='follower',
        cascade='all, delete-orphan',
        foreign_keys=[Follower.follower_id],
    )
    following: Mapped[List["Follower"]] = relationship(
        lazy='joined',
        back_populates='following',
        cascade='all, delete-orphan',
        foreign_keys=[Follower.following_id],
    )

    liked_tweets: Mapped[List["TweetLike"]] = relationship(
        lazy='joined',
        back_populates='user',
        cascade='all, delete-orphan',
    )

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'followers': [f.to_json() for f in self.followers],
            'following': [f.to_json() for f in self.following],
        }
