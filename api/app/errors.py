from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class NotFoundError(HTTPException):
    def __init__(self, details: str):
        super().__init__(404, details)


class NotUniqueError(HTTPException):
    def __init__(self, details: str):
        super().__init__(409, details)


async def default_http_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "status": exc.status_code,
            "title": "Invalid request",
            "message": exc.detail,
        },
    )


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content={"status": 400, "title": "Invalid request", "message": str(exc)},
    )


async def not_found_error_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        headers=exc.headers,
        content={"status": 404, "title": "Not found", "message": exc.detail},
    )


async def not_unique_error_handler(request: Request, exc: NotUniqueError):
    return JSONResponse(
        status_code=400,
        headers=exc.headers,
        content={
            "status": 400,
            "title": "Value not unique",
            "message": exc.detail,
        },
    )


async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={
            "status": 400,
            "title": "Validation error",
            "message": exc.args[0] if len(exc.args) > 0 else "Unexpected error",
        },
    )


def register_error_handlers(app):
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(NotUniqueError, not_unique_error_handler)
    app.add_exception_handler(NotFoundError, not_found_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(HTTPException, default_http_error_handler)
