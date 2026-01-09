from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class CreatedByMixin:
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
