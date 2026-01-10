from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.comment_crud import (
    CommentCRUD,
)
from app.crud.part_crud import PartCRUD
from app.database import get_db_session
from app.models.comment_model import CommentModel
from app.models.part_model import PartModel
from app.schemas.base_schemas import PaginatedResponseSchema
from app.schemas.comment_schemas import (
    CommentBaseSchema,
    CommentCreateSchema,
    CommentSchema,
)
from app.schemas.part_schemas import PartCreateSchema, PartSchema, PartUpdateSchema
from app.utils.get_current_user import get_current_user
from app.utils.get_part_exist import get_part_exist

app_router = APIRouter()


# Returns a paginated list of parts
@app_router.get("/parts", response_model=PaginatedResponseSchema[PartSchema])
def get_parts(
    db_session: Session = Depends(get_db_session),
    offset: int | None = None,
    limit: int | None = None,
) -> PaginatedResponseSchema[PartModel]:
    return PartCRUD.get_paginated_list(
        db_session=db_session, limit=limit, offset=offset
    )


# Creates a new part
@app_router.post("/parts", response_model=PartSchema)
def create_part(
    input: PartCreateSchema,
    db_session: Session = Depends(get_db_session),
    current_user=Depends(get_current_user),
) -> PartModel:
    return PartCRUD.create(
        db_session=db_session, input=input, current_user=current_user
    )


# Returns a specific part by its ID
@app_router.get("/parts/{part_id}", response_model=PartSchema)
def get_part(
    part_id: UUID,
    db_session: Session = Depends(get_db_session),
) -> PartModel:
    return PartCRUD.get_one_by(db_session=db_session, key="id", value=str(part_id))


# Updates a specific part by its ID
@app_router.put("/parts/{part_id}", response_model=PartSchema)
def update_part(
    part_id: UUID,
    input: PartUpdateSchema,
    db_session: Session = Depends(get_db_session),
    current_user=Depends(get_current_user),
) -> PartModel:
    return PartCRUD.update(
        db_session=db_session, entity_id=part_id, input=input, current_user=current_user
    )


# Returns all comments associated with the given part
@app_router.get("/parts/{part_id}/comments", response_model=list[CommentSchema])
def get_part_comments(
    part: PartModel = Depends(get_part_exist),
    db_session: Session = Depends(get_db_session),
) -> list[CommentModel]:
    return CommentCRUD.get_all_by(
        db_session=db_session, key="part_id", value=str(part.id)
    )


# Creates a new comment for the specified part
@app_router.post("/parts/{part_id}/comments", response_model=CommentSchema)
def create_part_comment(
    input: CommentBaseSchema,
    part: PartModel = Depends(get_part_exist),
    db_session: Session = Depends(get_db_session),
    current_user=Depends(get_current_user),
) -> CommentModel:
    input_data = CommentCreateSchema.model_validate(
        {
            **input.model_dump(),
            "part_id": part.id,
        }
    )
    return CommentCRUD.create(
        db_session=db_session, input=input_data, current_user=current_user
    )
