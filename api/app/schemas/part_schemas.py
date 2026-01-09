from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field

from app.schemas.base_schemas import AppBaseSchema

AnnotatedName = Annotated[
    str,
    Field(
        min_length=1,
        max_length=256,  # SQL String(256)
    ),
]

AnnotatedDescription = Annotated[
    str | None,
    Field(
        default=None,
        max_length=1024,  # SQL String(1024)
    ),
]


class PartBaseSchema(AppBaseSchema):
    name: AnnotatedName
    description: AnnotatedDescription = None


class PartCreateSchema(PartBaseSchema):
    pass


class PartUpdateSchema(AppBaseSchema):
    name: AnnotatedName | None = None
    description: AnnotatedDescription = None


class PartSchema(PartBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: UUID
