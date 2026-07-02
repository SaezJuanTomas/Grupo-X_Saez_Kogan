from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..core.logging import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    def __init__(self, message: str, code: str = "internal_error", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code


class ResourceNotFoundError(AppError):
    def __init__(self, message: str = "Recurso no encontrado"):
        super().__init__(message, code="not_found", status_code=404)


class DuplicateResourceError(AppError):
    def __init__(self, message: str = "El recurso ya existe"):
        super().__init__(message, code="duplicate", status_code=409)


class BusinessRuleError(AppError):
    def __init__(self, message: str = "Regla de negocio violada"):
        super().__init__(message, code="business_rule_violation", status_code=400)


class AuthenticationError(AppError):
    def __init__(self, message: str = "No autenticado"):
        super().__init__(message, code="authentication_error", status_code=401)


class AuthorizationError(AppError):
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message, code="authorization_error", status_code=403)


def build_error_response(
    code: str,
    message: str,
    request_id: str | None = None,
    fields: list[dict] | None = None,
) -> dict:
    error: dict = {"code": code, "message": message}
    if request_id:
        error["request_id"] = request_id
    if fields:
        error["fields"] = fields
    return {"error": error}


async def app_error_handler(request: Request, exc: AppError):
    logger.warning(f"{exc.code}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_response(exc.code, exc.message),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    code_map = {
        400: "bad_request",
        401: "authentication_error",
        403: "authorization_error",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
        422: "validation_error",
        429: "rate_limit_exceeded",
        500: "internal_error",
    }
    code = code_map.get(exc.status_code, "http_error")
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_response(code, str(exc.detail)),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    fields = [
        {
            "field": ".".join(str(x) for x in err.get("loc", [])),
            "message": err.get("msg", "Error de validación"),
            "type": err.get("type", "unknown"),
        }
        for err in exc.errors()
    ]
    logger.warning(f"Validation error: {fields}")
    return JSONResponse(
        status_code=422,
        content=build_error_response(
            "validation_error",
            "Los datos enviados no son válidos",
            fields=fields,
        ),
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=build_error_response("internal_error", "Error interno del servidor"),
    )


def register_exception_handlers(app):
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
