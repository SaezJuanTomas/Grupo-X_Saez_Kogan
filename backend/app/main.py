import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .core.config import config
from .core.exceptions import register_exception_handlers
from .core.logging import LoggingMiddleware, setup_logging
from .core.rate_limit import limiter
from .database import Base, SessionLocal, engine
from .routers import (
    auth_router,
    comment_router,
    company_router,
    history_router,
    n8n_router,
    statistics_router,
    user_router,
    vulnerability_router,
)
from .seed import seed_database

setup_logging(config.LOG_LEVEL)

app = FastAPI(title="Grupo X API - Gestión de Vulnerabilidades", version="2.0.0", docs_url="/docs", redoc_url="/redoc")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)

register_exception_handlers(app)


@app.on_event("startup")
def on_startup() -> None:
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_database(db)
            logging.getLogger("app").info("Database seeded successfully")
        finally:
            db.close()
    except Exception as e:
        logging.getLogger("app").warning(f"Database initialization skipped: {e}")


@app.get("/health")
def health():
    try:
        db = SessionLocal()
        db.execute(db.bind.dialect.statement_compiler(db.bind, db.bind.dialect().select_1()).__class__.__name__)
        db_status = "ok"
        db.close()
    except Exception:
        db_status = "error"
    return {"status": "ok", "database": db_status, "version": "2.0.0"}


app.include_router(auth_router.router)
app.include_router(vulnerability_router.router)
app.include_router(company_router.router)
app.include_router(user_router.router)
app.include_router(comment_router.router)
app.include_router(history_router.router)
app.include_router(statistics_router.router)
app.include_router(n8n_router.router)
