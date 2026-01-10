from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.comment_crud import CommentCRUD
from app.database import get_db_session
from app.models.comment_model import CommentModel
from app.routers.part_router import get_part_exist
from app.schemas.base_schemas import PaginatedResponseSchema
from app.schemas.comment_schemas import (
    CommentCreateSchema,
    CommentSchema,
    CommentUpdateSchema,
)
from app.utils.get_comment_exist import get_comment_exist
from app.utils.get_current_user import get_current_user

app_router = APIRouter()


# Returns a paginated list of comments
@app_router.get("/comments", response_model=PaginatedResponseSchema[CommentSchema])
def get_comments(
    db_session: Session = Depends(get_db_session),
    offset: int | None = None,
    limit: int | None = None,
) -> PaginatedResponseSchema[CommentModel]:
    return CommentCRUD.get_paginated_list(
        db_session=db_session, limit=limit, offset=offset
    )


# Creates a new comment
@app_router.post("/comments", response_model=CommentSchema)
def create_comment(
    input: CommentCreateSchema,
    db_session: Session = Depends(get_db_session),
    current_user=Depends(get_current_user),
) -> CommentModel:
    # check part is exist
    # if there is no exist part, the function will exception
    # with status 404 Not Found
    get_part_exist(part_id=input.part_id, db_session=db_session)

    return CommentCRUD.create(
        db_session=db_session, input=input, current_user=current_user
    )


# Updates a specific comment by its ID
@app_router.put("/comments/{comment_id}", response_model=CommentSchema)
def update_comment(
    input: CommentUpdateSchema,
    comment: CommentModel = Depends(get_comment_exist),
    db_session: Session = Depends(get_db_session),
    current_user=Depends(get_current_user),
) -> CommentModel:
    return CommentCRUD.update(
        db_session=db_session,
        entity_id=comment.id,
        input=input,
        current_user=current_user,
    )
