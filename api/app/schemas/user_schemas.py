from datetime import UTC, datetime
from uuid import UUID

from pydantic import AwareDatetime, Field

from app.schemas.comment_schemas import AppBaseSchema


class UserBaseSchema(AppBaseSchema):
    id: UUID
    name: str
    role: str
    is_active: bool | None = None


class UserSchema(UserBaseSchema):
    last_login_at: AwareDatetime
    created_at: AwareDatetime


class UserCreateSchema(AppBaseSchema):
    name: str
    role: str
    last_login_at: AwareDatetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class UserUpdateSchema(AppBaseSchema):
    name: str | None
    role: str | None
    is_active: bool | None
    last_login_at: AwareDatetime = Field(default_factory=lambda: datetime.now(tz=UTC))
