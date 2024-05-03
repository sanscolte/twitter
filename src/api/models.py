from typing import List

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


class Tweet(Base):
    __tablename__ = 'tweet'

    data: Mapped[str]
    media_ids: Mapped[List[int] | None] = mapped_column(ARRAY(String), nullable=True)


class Media(Base):
    __tablename__ = 'media'

    file: Mapped[str]
