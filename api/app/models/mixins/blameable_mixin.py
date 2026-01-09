from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.mixins.created_at_mixin import CreatedAtMixin
from app.models.mixins.created_by_mixin import CreatedByMixin


class BlameableMixin(CreatedAtMixin, CreatedByMixin):
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    updated_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
