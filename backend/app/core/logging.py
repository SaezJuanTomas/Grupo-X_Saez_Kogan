import logging
import sys
import time
import uuid

from fastapi import Request, Response
from starlette.types import ASGIApp, Receive, Scope, Send


def setup_logging(level: str = "INFO") -> None:
    logger = logging.getLogger("app")
    if logger.handlers:
        return

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"app.{name}")


EXCLUDED_PATHS = {"/health", "/favicon.ico", "/openapi.json", "/docs", "/redoc"}


class LoggingMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid.uuid4())
        scope["request_id"] = request_id

        request = Request(scope)
        path = request.url.path
        if path in EXCLUDED_PATHS or path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi"):
            await self.app(scope, receive, send)
            return

        logger = get_logger("http")
        start = time.time()
        logger.info("-> %s %s [id=%s] from=%s ua=%s", request.method, path, request_id, request.client.host if request.client else "unknown", request.headers.get("user-agent", ""))

        async def send_with_id(message):
            if message["type"] == "http.response.start":
                elapsed = (time.time() - start) * 1000
                original_headers = message.get("headers", [])
                headers = list(original_headers)
                headers.append((b"X-Request-ID", request_id.encode()))
                headers.append((b"X-Response-Time-ms", f"{elapsed:.1f}".encode()))
                message["headers"] = headers
                status = message.get("status", 0)
                level = "WARNING" if status >= 500 else ("INFO" if status < 400 else "WARNING")
                getattr(logger, level.lower())("<- %s %s [id=%s] %d in %.1fms", request.method, path, request_id, status, elapsed)
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        except Exception as exc:
            elapsed = (time.time() - start) * 1000
            logger.error("X %s %s [id=%s] ERROR in %.1fms: %s", request.method, path, request_id, elapsed, exc)
            raise
