from collections.abc import Generator

from sqlalchemy import Integer, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.settings import env

credentials = f"{env.db_user}:{env.db_password}"
host = f"{env.db_hostname}:{env.db_port}"
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{credentials}@{host}/{env.db_database}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"connect_timeout": 10})
DatabaseSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
DbSession = Session


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


def get_db_session() -> Generator[Session]:
    session = DatabaseSession()

    try:
        yield session
    finally:
        session.close()
