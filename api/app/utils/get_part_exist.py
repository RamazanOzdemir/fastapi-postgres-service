from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.crud.part_crud import PartCRUD
from app.database import get_db_session
from app.models.part_model import PartModel


def get_part_exist(
    part_id: UUID, db_session: Session = Depends(get_db_session)
) -> PartModel:
    """
    Retrieves and validates the existence of a Part by its UUID.

    This function attempts to retrieve a Part using the provided ID.
    If no Part is found, it raises an HTTPException with status code 404 NOT FOUND.
    Otherwise, it returns the confirmed existing PartModel instance.
    """
    return PartCRUD.get_one_by(
        db_session=db_session, key=PartModel.id.key, value=str(part_id)
    )
