from app.crud.base_crud import BaseCRUD
from app.models.user_model import UserModel
from app.schemas.user_schemas import UserCreateSchema, UserSchema, UserUpdateSchema


class UserCRUD(BaseCRUD[UserModel, UserSchema, UserCreateSchema, UserUpdateSchema]):
    @classmethod
    def get_model(cls) -> type[UserModel]:
        return UserModel
