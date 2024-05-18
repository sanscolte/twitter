"""init migration

Revision ID: b80fb1108699
Revises: 
Create Date: 2024-05-11 21:27:03.567433

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b80fb1108699"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("api_key", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("api_key", "id"),
        sa.UniqueConstraint("api_key"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "follower",
        sa.Column("follower_api_key", sa.String(), nullable=False),
        sa.Column("following_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["follower_api_key"],
            ["user.api_key"],
        ),
        sa.ForeignKeyConstraint(
            ["following_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "follower_api_key",
            "following_id",
            name="uq_follower_api_key_following_id",
        ),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "tweet",
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("author_api_key", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["author_api_key"],
            ["user.api_key"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "media",
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("tweet_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(["tweet_id"], ["tweet.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "tweet_like",
        sa.Column("user_api_key", sa.String(), nullable=False),
        sa.Column("tweet_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(["tweet_id"], ["tweet.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_api_key"], ["user.api_key"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint(
            "user_api_key", "tweet_id", name="uq_user_api_key_tweet_id"
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("tweet_like")
    op.drop_table("media")
    op.drop_table("tweet")
    op.drop_table("follower")
    op.drop_table("user")
    # ### end Alembic commands ###