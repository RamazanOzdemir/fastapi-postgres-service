from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.models.mixins.blameable_mixin import BlameableMixin
from app.models.mixins.id_mixin import IdMixin
from app.models.part_model import PartModel


class CommentModel(BaseModel, IdMixin, BlameableMixin):
    __tablename__ = "comments"

    part_id: Mapped[UUID] = mapped_column(ForeignKey("parts.id"))
    content: Mapped[str] = mapped_column(String(2028))

    # Many-to-one relationship: each comment belongs to a single part
    part: Mapped[PartModel] = relationship("PartModel", back_populates="comments")

    # Relationship to the user who created the comment
    creator: Mapped[UserModel] = relationship(  # noqa: F821 # pyright: ignore[reportUndefinedVariable]
        "UserModel",
        foreign_keys="[CommentModel.created_by]",
        back_populates="comments",
        lazy="selectin",
    )
