from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import errors
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
