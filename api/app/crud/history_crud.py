from sqlalchemy.orm import Session

from app.models.history_model import HistoryModel
from app.schemas.history_schemas import HistoryCreateSchema


class HistoryCrud:
    @classmethod
    def create(
        cls, db_session: Session, input: HistoryCreateSchema, *, commit: bool = True
    ) -> HistoryModel:
        # model_dump mode needs to be json to enable i.e. UUID serialization
        new_entity = HistoryModel(**input.model_dump(mode="json"))
        db_session.add(new_entity)
        if commit:
            db_session.commit()
        else:
            db_session.flush()
        db_session.refresh(new_entity)
        return new_entity
