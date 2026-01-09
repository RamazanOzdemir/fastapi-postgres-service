from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.models.mixins.blameable_mixin import BlameableMixin
from app.models.mixins.id_mixin import IdMixin


class PartModel(BaseModel, IdMixin, BlameableMixin):
    __tablename__ = "parts"

    name: Mapped[str] = mapped_column(String(256), unique=True)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # One-to-many relationship: a part can have multiple comments
    comments: Mapped[list[CommentModel]] = relationship(  # noqa: F821 # pyright: ignore[reportUndefinedVariable]
        "CommentModel", back_populates="part", cascade="all, delete-orphan"
    )
