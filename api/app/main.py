from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app import errors, settings
from app.database import DbSession, get_db_session
from app.routers import comment_router, part_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup logic (ileride)
    yield
    # shutdown logic (ileride)


app = FastAPI(
    title="FastAPI Postgres Service",
    version="0.1.0",
    lifespan=lifespan,
    root_path="/api",
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["*"],
)

errors.register_error_handlers(app)

app.include_router(part_router.app_router)
app.include_router(comment_router.app_router)


@app.get("/health-check", tags=["Health"])
def health_check(
    db_session: Annotated[DbSession, Depends(get_db_session)],
) -> dict:
    res = db_session.execute(
        text("SELECT version_num from alembic_version LIMIT 1")
    ).fetchone()

    if res is None:
        raise HTTPException(
            status_code=503,
            detail="Database is reachable but Alembic version table is empty",
        )

    return {
        "status": "ok",
        "app": {"version": settings.env.app_version},
        "db": {"version": res[0]},
    }
