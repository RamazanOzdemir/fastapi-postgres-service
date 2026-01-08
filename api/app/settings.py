import pathlib
from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict

backend_directory = pathlib.Path(__file__).parent.parent


class EnvMode(Enum):
    DEV = "DEV"
    TEST = "TEST"
    PROD = "PROD"


class Settings(BaseSettings):
    app_name: str = "Applicant Task"
    app_version: str = "0.0.0"
    env_mode: EnvMode = EnvMode.DEV
    cookie_domain: str = "localhost"

    filestore_path: str = str(backend_directory.parent.joinpath("filestore"))

    smtp_host: str = "mailhog"
    smtp_port: int = 1025

    db_user: str = "postgres"
    db_password: str = "password"
    db_hostname: str = "applicant-task-db"
    db_database: str = "applicant-task"
    db_port: int = 7831

    model_config = SettingsConfigDict(
        env_file=pathlib.Path(__file__).parent.parent.joinpath(".env")
    )


env = Settings()
