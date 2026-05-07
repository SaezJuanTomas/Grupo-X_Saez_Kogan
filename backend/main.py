from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import auth, vulnerabilities, users, comments, history

# Crear las tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gestión de Vulnerabilidades",
    description="API para gestión de vulnerabilidades de ciberseguridad",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # URLs del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["autenticación"])
app.include_router(vulnerabilities.router, prefix="/vulnerabilidades", tags=["vulnerabilidades"])
app.include_router(users.router, prefix="/usuarios", tags=["usuarios"])
app.include_router(comments.router, prefix="/comentarios", tags=["comentarios"])
app.include_router(history.router, prefix="/historial", tags=["historial"])

@app.get("/")
async def root():
    return {"message": "API de Gestión de Vulnerabilidades", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}