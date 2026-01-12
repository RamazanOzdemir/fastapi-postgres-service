from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.main import app, get_db_session
from app.models.base_model import BaseModel
from app.models.user_model import UserModel
from app.settings import EnvMode, Settings
from app.utils.get_current_user import get_current_user

# The fixed ID for testing system/default user
TEST_ALICE_ID = UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """
    Returns application settings configured for the test environment.
    Uses 'applicant-task-db' as hostname for Docker networking.
    """

    class TestSettings(Settings):
        env_mode: EnvMode = EnvMode.TEST
        db_user: str = "postgres"
        db_password: str = "password"
        db_hostname: str = "app-net-db"
        db_database: str = "app_net_test"
        db_port: int = 7831

    return TestSettings()


@pytest.fixture(scope="session")
def db_engine(test_settings: Settings):
    """
    Creates the SQLAlchemy Engine once per test session.
    Creates all tables before tests and drops them after the session ends.
    """

    credentials = f"{test_settings.db_user}:{test_settings.db_password}"
    host = f"{test_settings.db_hostname}:{test_settings.db_port}"
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+psycopg://{credentials}@{host}/{test_settings.db_database}"
    )

    engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)

    # Create all tables before the session starts
    BaseModel.metadata.create_all(bind=engine)

    yield engine
    # Drop all tables after the session ends
    BaseModel.metadata.drop_all(bind=engine)

    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """
    Creates a new isolated DB session and transaction for every test.
    All changes are rolled back automatically at the end of the test (Isolation).
    """
    session_local = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine, expire_on_commit=False
    )

    session = session_local()
    session.begin()

    try:
        # Yield the session object to the test function
        yield session

    finally:
        session.rollback()

        # 3. Close the session: Release the connection back to the pool
        session.close()


@pytest.fixture
def current_user(db_session: Session) -> UserModel:
    """
    Creates the 'Alice' user in the test database to simulate the result
    of the get_current_user dependency.
    """
    user_id = uuid4()

    alice = UserModel(
        id=user_id,
        name="Alice",
        role="admin",
        is_active=True,
    )

    db_session.add(alice)

    db_session.flush()

    return alice


@pytest.fixture
def client(db_session: Session, current_user: UserModel):
    """
    Overrides the FastAPI dependencies (DB Session and Current User)
    to use the isolated test fixtures.
    """

    def override_get_db_session():
        """
        Overrides the standard get_db_session to provide the test transaction session.
        """
        yield db_session

    def override_get_current_user():
        """
        Overrides the standard get_current_user to provide the mocked user object.
        """

        return current_user

    # Apply overrides
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as client:
        yield client

    # Cleanup: Remove overrides after the test is done
    app.dependency_overrides.pop(get_db_session)
    app.dependency_overrides.pop(get_current_user)
