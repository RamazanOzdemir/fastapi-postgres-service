import json
from typing import Any
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSON, JSONB
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

from app.models.base_model import BaseModel
from app.models.mixins.created_at_mixin import CreatedAtMixin
from app.models.mixins.id_mixin import IdMixin
from app.schemas.history_schemas import HistoryAction, ValueChangeSchema


class ChangesJSON(TypeDecorator[dict[str, Any]]):
    impl = JSONB

    def process_bind_param(  # noqa: PLR6301
        self, value: dict[str, Any] | None, dialect: Dialect
    ) -> str | None:
        if value is None:
            return None

        # ensure each value in the dict is valid ValueChangeSchema
        try:
            for val in value.values():
                ValueChangeSchema(**val)
        except ValueError as e:
            raise ValueError(f"Invalid JSON format: {e}")

        return json.dumps(value)

    def process_result_value(  # noqa: PLR6301
        self, value: Any, dialect: Dialect
    ) -> dict[str, Any] | None:
        if isinstance(value, str):
            return json.loads(value)
        return value


class HistoryModel(BaseModel, IdMixin, CreatedAtMixin):
    """
    Table to keep track of changes to the DB
    """

    __tablename__ = "history"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    table_name: Mapped[str]
    entity_id: Mapped[UUID]
    action: Mapped[HistoryAction]
    changes: Mapped[JSON] = mapped_column(ChangesJSON)
