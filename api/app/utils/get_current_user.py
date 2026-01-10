from fastapi import Depends
from sqlalchemy.orm import Session

from app.crud.user_crud import UserCRUD
from app.database import get_db_session
from app.models.user_model import UserModel

###
# This is a stub for getting the current user. In a real application, this would
# involve authentication logic such as decoding a JWT token.
###


def get_current_user(db_session: Session = Depends(get_db_session)) -> UserModel:
    return UserCRUD.get_one_by(
        db_session=db_session, key=UserModel.name.key, value="Alice"
    )
