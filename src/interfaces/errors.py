from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# domain
from application.ports import *


def _msg(exc: Exception, fallback: str) -> str:
    # Prefer a custom .detail if your exceptions define it; else str(exc); else fallback
    return getattr(exc, "detail", None) or (str(exc) if str(exc) else fallback)


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def request_validation(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    # Optional: keep default behavior for HTTPException (status + detail)
    @app.exception_handler(StarletteHTTPException)
    async def http_exc(request: Request, exc: StarletteHTTPException):
        # FastAPI already does this, but having it here ensures consistency
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(NotFound)
    async def not_found(request: Request, exc: NotFound):
        return JSONResponse(status_code=404, content={"detail": _msg(exc, "Not found")})

    @app.exception_handler(AlreadyExists)
    async def already_exists(request: Request, exc: AlreadyExists):
        return JSONResponse(status_code=409, content={"detail": _msg(exc, "Already exists")})

    @app.exception_handler(Unauthorized)
    async def unauthorized(request: Request, exc: Unauthorized):
        return JSONResponse(status_code=401, content={"detail": _msg(exc, "Unauthorized")})

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception):
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
