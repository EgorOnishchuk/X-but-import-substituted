import uuid

from sqlalchemy import Column, ForeignKey, String, Table, Uuid
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import SQLAlchemyIDModel, SQLAlchemyModel
from src.users.models import SQLAlchemyUser


class SQLAlchemyTweet(SQLAlchemyIDModel):
    __readable_name__ = "tweet"
    __tablename__ = "tweets"

    text: Mapped[str] = mapped_column(String(500))
    medias: Mapped[list[uuid.UUID]] = mapped_column(ARRAY(Uuid))
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", onupdate="RESTRICT", ondelete="CASCADE")
    )

    author: Mapped[SQLAlchemyUser] = relationship("SQLAlchemyUser")
    likes: Mapped[list[SQLAlchemyUser]] = relationship(
        "SQLAlchemyUser", secondary="likes"
    )


sqlalchemy_likes: Table = Table(
    "likes",
    SQLAlchemyModel.metadata,
    Column(
        "tweet_id",
        Uuid,
        ForeignKey("tweets.id", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "user_id",
        Uuid,
        ForeignKey("users.id", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    ),
)
