from app.crud.base_crud import BaseCRUD
from app.models.comment_model import CommentModel
from app.schemas.comment_schemas import (
    CommentCreateSchema,
    CommentSchema,
    CommentUpdateSchema,
)


class CommentCRUD(
    BaseCRUD[CommentModel, CommentSchema, CommentCreateSchema, CommentUpdateSchema]
):
    # Related fields to refresh after create/update operations
    related_to_refresh = ["creator"]

    @classmethod
    def get_model(cls) -> type[CommentModel]:
        return CommentModel
