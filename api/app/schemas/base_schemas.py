from typing import TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class AppBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponseSchema[T](BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    offset: int | None
    limit: int | None
    total: int
    data: list[T]
