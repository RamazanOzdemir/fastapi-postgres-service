import pytest
from sqlalchemy.orm import Session

from app.crud.comment_crud import CommentCRUD
from app.crud.part_crud import PartCRUD
from app.models.part_model import PartModel
from app.models.user_model import UserModel
from tests.utils import create_safe_patch


@pytest.fixture
def mock_parts(db_session: Session, current_user: UserModel) -> dict[str, PartModel]:
    # Default Parts Data
    default_part_first = PartModel(
        name="Part A",
        description="Part A description",
        updated_by=current_user.id,
        created_by=current_user.id,
    )
    default_part_second = PartModel(
        name="Part B",
        description="Part B description",
        updated_by=current_user.id,
        created_by=current_user.id,
    )

    db_session.add_all([default_part_first, default_part_second])

    # to assign ID to new parts
    db_session.flush()

    return {
        "part_a": default_part_first,
        "part_b": default_part_second,
    }


@pytest.fixture
def mock_crud_no_commit():
    """
    Patches all persistence methods for CRUD
    to force commit=False.
    """

    # List all methods to be patched for PartCRUD and
    patches = [
        create_safe_patch(PartCRUD, "create"),
        create_safe_patch(PartCRUD, "update"),
        create_safe_patch(CommentCRUD, "create"),
    ]

    # SETUP: Start all patches
    for p in patches:
        p.start()

    yield

    # TEARDOWN: Stop and restore original methods
    for p in reversed(patches):
        p.stop()
