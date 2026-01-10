from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.crud.comment_crud import CommentCRUD
from app.database import get_db_session
from app.models.comment_model import CommentModel


def get_comment_exist(
    comment_id: UUID, db_session: Session = Depends(get_db_session)
) -> CommentModel:
    """
    Retrieves and validates the existence of a Comment by its UUID.

    This function attempts to retrieve a Comment using the provided ID.
    If no Comment is found, it raises an HTTPException with status code 404 NOT FOUND.
    Otherwise, it returns the confirmed existing CommentModel instance.
    """
    return CommentCRUD.get_one_by(
        db_session=db_session, key=CommentModel.id.key, value=str(comment_id)
    )
