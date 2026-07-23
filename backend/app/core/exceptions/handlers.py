from fastapi import Request
from fastapi.responses import JSONResponse

from app.application.exceptions import ApplicationError, ConflictError, NotFoundError, UnauthorizedError
from app.domain.shared.exceptions import DomainError


async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"code": exc.code, "message": exc.message})


async def application_error_handler(_: Request, exc: ApplicationError) -> JSONResponse:
    status_map = {
        "NOT_FOUND": 404,
        "CONFLICT": 409,
        "UNAUTHORIZED": 401,
    }
    status_code = status_map.get(exc.code, 400)
    return JSONResponse(status_code=status_code, content={"code": exc.code, "message": exc.message})
