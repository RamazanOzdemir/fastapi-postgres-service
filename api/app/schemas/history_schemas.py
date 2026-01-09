from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import field_validator

from app.schemas.base_schemas import AppBaseSchema


class HistoryAction(Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class ValueChangeSchema(AppBaseSchema):
    old: Any
    new: Any

    @field_validator("old", "new", mode="before")
    def convert_orm_to_dict(cls, v):  # noqa: N805
        # Check if the value is a SQLAlchemy ORM instance
        if hasattr(v, "__mapper__"):  # It's an ORM object
            # If the model has a Pydantic schema with model_validate, use it
            if hasattr(v.__class__, "model_validate"):
                return v.__class__.model_validate(v).model_dump()
            # Otherwise, convert all table columns to a dictionary
            return {
                column.key: getattr(v, column.key) for column in v.__table__.columns
            }
        # If it's not an ORM instance, return it as is
        return v


class HistoryCreateSchema(AppBaseSchema):
    table_name: str
    entity_id: UUID
    user_id: UUID
    action: str
    changes: dict[str, ValueChangeSchema]


class HistoryReadSchema(AppBaseSchema):
    id: UUID
    user_id: UUID
    action: str
    changes: dict[str, ValueChangeSchema]
    created_at: datetime
