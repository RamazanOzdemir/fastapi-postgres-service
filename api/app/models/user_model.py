from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.models.mixins.created_at_mixin import CreatedAtMixin
from app.models.mixins.id_mixin import IdMixin


class UserModel(BaseModel, IdMixin, CreatedAtMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(unique=True)
    role: Mapped[str]
    is_active: Mapped[bool | None] = mapped_column(default=True)
    last_login_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # fmt: off
    comments: Mapped[list[CommentModel]] = relationship(  # noqa: F821 # pyright: ignore[reportUndefinedVariable]
        "CommentModel",
        primaryjoin="UserModel.id == CommentModel.created_by",
        back_populates="creator",
        cascade="all, delete-orphan",
    )
    # fmt: on
