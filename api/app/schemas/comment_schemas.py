from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field

from app.schemas.base_schemas import AppBaseSchema
from app.schemas.user_schemas import UserBaseSchema

AnnotatedContent = Annotated[
    str,
    Field(
        min_length=1,
        max_length=2028,  # SQL String(2028)
    ),
]


class CommentBaseSchema(AppBaseSchema):
    content: AnnotatedContent


class CommentCreateSchema(CommentBaseSchema):
    part_id: UUID


class CommentUpdateSchema(AppBaseSchema):
    content: AnnotatedContent


class CommentSchema(CommentBaseSchema):
    id: UUID
    part_id: UUID
    created_by: UUID
    updated_by: UUID | None = None
    created_at: datetime
    updated_at: datetime
    creator: UserBaseSchema
