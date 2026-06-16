from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app = FastAPI(title="Grupo X API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router.router)
app.include_router(vulnerability_router.router)
app.include_router(company_router.router)
app.include_router(user_router.router)
app.include_router(comment_router.router)
app.include_router(history_router.router)
app.include_router(statistics_router.router)
app.include_router(n8n_router.router)
