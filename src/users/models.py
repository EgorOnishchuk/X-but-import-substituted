from sqlalchemy import Column, ForeignKey, String, Table, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import SQLAlchemyIDModel, SQLAlchemyModel


class SQLAlchemyUser(SQLAlchemyIDModel):
    __readable_name__ = "user"
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(30), unique=True)
    key: Mapped[str] = mapped_column(String(64))

    following: Mapped[list["SQLAlchemyUser"]] = relationship(
        "SQLAlchemyUser",
        secondary="follows",
        primaryjoin="SQLAlchemyUser.id == follows.c.follower_id",
        secondaryjoin="SQLAlchemyUser.id == follows.c.followed_id",
        backref="followers",
    )


sqlalchemy_follows: Table = Table(
    "follows",
    SQLAlchemyModel.metadata,
    Column(
        "follower_id",
        Uuid,
        ForeignKey("users.id", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "followed_id",
        Uuid,
        ForeignKey("users.id", onupdate="RESTRICT", ondelete="CASCADE"),
        primary_key=True,
    ),
)
