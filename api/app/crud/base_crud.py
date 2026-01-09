from datetime import UTC, datetime
from typing import Any, TypeVar
from uuid import UUID

from fastapi import HTTPException
from psycopg.errors import UniqueViolation
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import String, and_, cast, func, inspect, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query, Session
from sqlalchemy.sql.elements import ColumnElement

from app.crud.history_crud import HistoryCrud
from app.errors import NotFoundError, NotUniqueError
from app.models.base_model import BaseModel
from app.models.mixins.blameable_mixin import BlameableMixin
from app.models.mixins.created_by_mixin import CreatedByMixin
from app.models.mixins.id_mixin import IdMixin
from app.models.mixins.soft_deletable_mixin import SoftDeletableMixin
from app.models.user_model import UserModel
from app.schemas.base_schemas import PaginatedResponseSchema
from app.schemas.history_schemas import (
    HistoryAction,
    HistoryCreateSchema,
    ValueChangeSchema,
)

ModelType = TypeVar("ModelType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=PydanticBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=PydanticBaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=PydanticBaseModel | None)


class BaseCRUD[
    ModelType: BaseModel,
    SchemaType: PydanticBaseModel,
    CreateSchemaType: PydanticBaseModel,
    UpdateSchemaType: PydanticBaseModel | None,
]:
    # model fields that should be used during global search
    searchable_fields: list[str] = []
    # List of related fields to refresh after create/update operations
    related_to_refresh: list[str] = []

    @classmethod
    def get_model(cls) -> type[ModelType]:
        raise NotImplementedError

    @classmethod
    def __apply_filters__(
        cls,
        query: Query[ModelType],
        filters: dict[str, str | list[str]] | None,
        *,
        and_operator: bool = True,  # if false, then we or the conditions together (used for global search)
    ) -> Query[ModelType]:
        # Always filter out soft-deleted entities
        model = cls.get_model()
        if issubclass(model, SoftDeletableMixin):
            query = query.filter(model.deleted_at.is_(None))

        if not filters:
            return query

        # Collect all the filters to apply an OR condition at the end
        conditions: list[ColumnElement[bool]] = []

        for key, value in filters.items():
            if "." in key:
                # Handling parent property filtering
                relationship, sub_property = key.split(".", 1)
                if not hasattr(model, relationship):
                    raise AttributeError(
                        f"Model {model.__name__} has no relationship {relationship}"
                    )

                related_model = getattr(model, relationship).property.mapper.class_
                if not hasattr(related_model, sub_property):
                    raise AttributeError(
                        f"Related model {related_model.__name__} has no attribute {sub_property}"
                    )

                if not any(
                    table[0].fullname == related_model.__tablename__  # type: ignore
                    for table in query._setup_joins
                ):
                    query = query.join(related_model)
                model_value = getattr(related_model, sub_property)
            else:
                if not hasattr(model, key):
                    raise AttributeError(
                        f"Model {model.__name__} has no attribute {key}"
                    )
                model_value = getattr(model, key)

            # if filter value is string containing , split it into list, trim all values
            # and replace spaces with % to allow for more liberal search
            if isinstance(value, str) and "," in value:
                values = [v.strip().replace(" ", "%") for v in value.split(",")]
                conditions.append(
                    or_(*[cast(model_value, String).ilike(f"%{v}%") for v in values])
                )
            elif isinstance(value, list):
                # When receiving a list of values, we want to filter for case-insensitive
                # matches, because we assume the user used a multi-select filter in the
                # frontend.
                # the only thing we do is additionally search for the value with
                # underscores instead of spaces.
                conditions.append(
                    or_(
                        *[
                            or_(model_value.is_(None))
                            if v == "NULL"
                            else or_(
                                cast(model_value, String).ilike(f"{str(v)}"),
                                cast(model_value, String).ilike(
                                    f"{str(v).replace(' ', '_')}"
                                ),
                            )
                            for v in value
                        ]
                    )
                )
            elif value == "NULL":
                conditions.append(model_value.is_(None))
            elif not value:
                continue
            else:
                formatted_value = str(value).replace(" ", "%")
                conditions.append(
                    cast(model_value, String).ilike(f"%{formatted_value}%")
                )

        # Apply all the conditions as either AND or OR
        if conditions and and_operator:
            query = query.filter(and_(*conditions))
        elif conditions:
            query = query.filter(or_(*conditions))

        return query

    @classmethod
    def __apply_sorting__(
        cls, query: Query[ModelType], sorting: dict[str, str] | None
    ) -> Query[ModelType]:
        model = cls.get_model()
        if sorting:
            for key, value in sorting.items():
                model_class: type[BaseModel] = model
                model_property = key

                if "." in key:
                    # Handling parent property filtering
                    relationship, sub_property = key.split(".", 1)
                    if not hasattr(model, relationship):
                        raise AttributeError(
                            f"Model {model.__name__} has no relationship {relationship}"
                        )

                    model_class = getattr(model, relationship).property.mapper.class_
                    if not hasattr(model_class, sub_property):
                        raise AttributeError(
                            f"Related model {model_class.__name__} has no attribute {sub_property}"
                        )
                    model_property = sub_property

                    if not any(
                        table[0].fullname == model_class.__tablename__  # type: ignore
                        for table in query._setup_joins
                    ):
                        query = query.join(model_class)
                elif not hasattr(model, key):
                    raise AttributeError(f"Model {model} has no attribute {key}")

                if value.lower() == "asc":
                    query = query.order_by(getattr(model_class, model_property).asc())
                elif value.lower() == "desc":
                    query = query.order_by(getattr(model_class, model_property).desc())
                # order by shortest value (character length)
                elif value.lower() == "shortest":
                    query = query.order_by(
                        func.length(
                            cast(getattr(model_class, model_property or key), String)
                        ).asc()
                    )
                else:
                    raise ValueError(
                        f"Invalid sorting value '{value}'. Use 'asc' or 'desc'."
                    )
        elif hasattr(model, "created_at"):
            query = query.order_by(model.created_at.desc())  # type: ignore
        elif hasattr(model, "title"):
            query = query.order_by(model.title.asc())  # type: ignore
        elif hasattr(model, "id"):
            query = query.order_by(model.name.asc())  # type: ignore

        return query

    @classmethod
    def __apply_global_filter__(
        cls, query: Query[ModelType], global_filter: str | None
    ) -> Query[ModelType]:
        if not global_filter:
            return query

        filters: dict[str, str | list[str]] = {}
        for field in cls.searchable_fields:
            filters[field] = global_filter
        return cls.__apply_filters__(
            query,
            filters,
            and_operator=False,  # OR the conditions together (if any field matches the search query)
        )

    @classmethod
    def __record_history__(
        cls,
        db_session: Session,
        action: HistoryAction,
        current_user: UserModel,
        after_action: ModelType | None = None,
        before_action: ModelType | dict[str, Any] = {},
        *,
        commit: bool = True,
    ) -> None:
        table_name = None
        if after_action:
            table_name = after_action.__tablename__
        elif before_action and isinstance(before_action, BaseModel):
            table_name = before_action.__tablename__

        if table_name is None:
            raise Exception("Can't record history. Table name is not available.")

        entity_id: UUID | None = None
        if after_action and isinstance(after_action, IdMixin):
            entity_id = after_action.id
        elif before_action and isinstance(before_action, IdMixin):
            entity_id = before_action.id

        if entity_id is None:
            raise Exception("Can't record history. Entity ID is not available.")

        changes: dict[str, ValueChangeSchema] = {}
        if after_action is None:
            if not isinstance(before_action, BaseModel):
                raise Exception(
                    "Can't record history. Before action is not a BaseModel instance."
                )
            for key in before_action.__dict__:
                if not key.startswith("_") and key not in {
                    "created_at",
                    "created_by",
                    "updated_at",
                    "updated_by",
                }:
                    # Ensure the value is not a relationship
                    mapper = inspect(before_action.__class__)
                    value = before_action.__dict__.get(key)
                    if key not in mapper.relationships and not isinstance(
                        value, BaseModel
                    ):
                        changes[key] = ValueChangeSchema(old=value, new=None)
        else:
            before_action_dict = (
                before_action.__dict__
                if isinstance(before_action, BaseModel)
                else before_action
            )
            after_action_dict = after_action.__dict__

            for key in after_action_dict:
                old_value = before_action_dict.get(key)
                new_value = after_action_dict.get(key)
                if (
                    not key.startswith("_")
                    and key
                    not in {
                        "created_at",
                        "created_by",
                        "updated_at",
                        "updated_by",
                    }
                    and old_value != new_value
                ):
                    changes[key] = ValueChangeSchema(old=old_value, new=new_value)

        HistoryCrud.create(
            db_session=db_session,
            input=HistoryCreateSchema(
                table_name=table_name,
                entity_id=entity_id,
                user_id=current_user.id,
                action=action.value,
                changes=changes,
            ),
            commit=commit,
        )

    @classmethod
    def get_all(cls, db_session: Session) -> list[ModelType]:
        query = db_session.query(cls.get_model())
        query = cls.__apply_filters__(query, None)
        return query.all()

    @classmethod
    def get_all_by(
        cls, db_session: Session, key: str, value: str | list[str]
    ) -> list[ModelType]:
        model = cls.get_model()
        if not hasattr(model, key):
            raise AttributeError(f"{model.__name__} has no attribute '{key}'")

        query = db_session.query(model)
        query = cls.__apply_filters__(query, {key: value})
        query = cls.__apply_sorting__(query, None)

        return query.all()

    @classmethod
    def get_one_or_null_by(
        cls, db_session: Session, key: str, value: str
    ) -> ModelType | None:
        if not hasattr(cls.get_model(), key):
            raise AttributeError(f"{cls.get_model().__name__} has no attribute '{key}'")
        query = db_session.query(cls.get_model()).filter(
            getattr(cls.get_model(), key) == value
        )
        return query.one_or_none()

    @classmethod
    def get_one_by(cls, db_session: Session, key: str, value: str) -> ModelType:
        entity = cls.get_one_or_null_by(db_session, key, value)
        if entity is None:
            raise NotFoundError(
                f"{cls.get_model().__name__} with {key}='{value}' was not found."
            )
        return entity

    @classmethod
    def get_paginated_list(
        cls,
        db_session: Session,
        offset: int | None,
        limit: int | None,
        filters: dict[str, str | list[str]] | None = None,
        sorting: dict[str, str] | None = None,
        global_filter: str | None = None,
    ) -> PaginatedResponseSchema[ModelType]:
        query = db_session.query(cls.get_model())
        query = cls.__apply_filters__(query, filters)
        query = cls.__apply_sorting__(query, sorting)
        query = cls.__apply_global_filter__(query, global_filter)

        total = query.count()

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        data = query.all()

        return PaginatedResponseSchema[ModelType](
            offset=offset, limit=limit, total=total, data=data
        )

    @classmethod
    def create(
        cls,
        db_session: Session,
        input: CreateSchemaType,
        current_user: UserModel,
        *,
        commit: bool = True,
    ) -> ModelType:
        new_entity = cls.get_model()(**input.model_dump(by_alias=True))

        if isinstance(new_entity, CreatedByMixin):
            new_entity.created_by = current_user.id
        if isinstance(new_entity, BlameableMixin):
            new_entity.updated_by = current_user.id

        db_session.add(new_entity)
        try:
            if commit:
                db_session.commit()
            else:
                db_session.flush()
        except IntegrityError as e:
            db_session.rollback()
            if isinstance(e.orig, UniqueViolation) and e.orig.diag.message_primary:
                # Return error message from diagnostics
                raise NotUniqueError(e.orig.diag.message_primary)
            raise e
        except ValueError as e:
            db_session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

        db_session.refresh(new_entity, cls.related_to_refresh)

        cls.__record_history__(
            db_session=db_session,
            action=HistoryAction.CREATE,
            after_action=new_entity,
            current_user=current_user,
            commit=commit,
        )

        return new_entity

    @classmethod
    def update(
        cls,
        db_session: Session,
        entity_id: UUID,
        input: UpdateSchemaType,
        current_user: UserModel,
        *,
        commit: bool = True,
    ) -> ModelType:
        if input is None:
            raise ValueError("Input is required for update operation.")

        entity = cls.get_one_by(db_session=db_session, key="id", value=str(entity_id))
        # copy entity to record history
        entity_copy = entity.__dict__.copy()

        if isinstance(entity, BlameableMixin):
            entity.updated_by = current_user.id

        # merge entity with input
        for key, value in input.model_dump(by_alias=True).items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        db_session.add(entity)

        if commit:
            db_session.commit()
        else:
            db_session.flush()

        db_session.refresh(entity)

        cls.__record_history__(
            db_session=db_session,
            action=HistoryAction.UPDATE,
            before_action=entity_copy,
            after_action=entity,
            current_user=current_user,
            commit=commit,
        )

        return entity

    @classmethod
    def soft_delete(
        cls,
        db_session: Session,
        entity_id: UUID,
        current_user: UserModel,
        *,
        commit: bool = True,
    ):
        model = cls.get_model()

        required_attributes = ["deleted_at", "deleted_by"]

        for attribute in required_attributes:
            if not hasattr(model, attribute):
                raise AttributeError(f"{model.__name__} has no attribute '{attribute}'")

        entity = cls.get_one_by(db_session=db_session, key="id", value=str(entity_id))

        if not isinstance(entity, SoftDeletableMixin):
            raise TypeError("Entity is not an instance of SoftDeletableMixin.")

        # copy entity before modification for history record
        entity_copy = entity.__dict__.copy()

        entity.deleted_at = datetime.now(UTC)
        entity.deleted_by = current_user.id

        db_session.add(entity)

        if commit:
            db_session.commit()
        else:
            db_session.flush()

        cls.__record_history__(
            db_session=db_session,
            action=HistoryAction.DELETE,
            before_action=entity_copy,
            after_action=entity,
            current_user=current_user,
            commit=commit,
        )
