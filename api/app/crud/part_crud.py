from app.crud.base_crud import BaseCRUD
from app.models.part_model import PartModel
from app.schemas.part_schemas import PartCreateSchema, PartSchema, PartUpdateSchema


class PartCRUD(BaseCRUD[PartModel, PartSchema, PartCreateSchema, PartUpdateSchema]):
    @classmethod
    def get_model(cls) -> type[PartModel]:
        return PartModel
