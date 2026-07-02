# Grupo X — Plataforma de Gestión de Vulnerabilidades

Sistema integral de gestión y automatización de vulnerabilidades de seguridad informática, con backend en FastAPI + PostgreSQL, frontend en React + TypeScript, y automatización inteligente mediante n8n.

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2.0 |
| Base de Datos | PostgreSQL 16 (Alembic para migraciones) |
| Frontend | React 18 + TypeScript + Vite + TailwindCSS |
| Automatización | n8n (workflows visuales) |
| Autenticación | JWT con refresh token rotation + bcrypt |
| Seguridad | Rate limiting (SlowAPI), CORS configurado, validación Pydantic v2 |
| Testing | Pytest + httpx (integración), Vitest + Testing Library (frontend) |
| Infraestructura | Docker Compose (PostgreSQL + n8n + pgAdmin) |

## Arquitectura

```
┌──────────┐     ┌──────────────────────────────────────────────────────────┐
│ Frontend │────▶│                    Backend (FastAPI)                     │
│ (React)  │     │  ┌─────────┐  ┌─────────┐  ┌────────────┐  ┌─────────┐  │
│ :5173    │     │  │ Routers │─▶│Services │─▶│Repositories│─▶│ Models  │  │
└──────────┘     │  └─────────┘  └─────────┘  └────────────┘  └─────────┘  │
       │         │                    │                                     │
       │         │              ┌─────┴──────┐                             │
       │         │              │  Logging +  │                             │
       │         │              │ Exception   │                             │
       │         │              │  Handlers   │                             │
       │         │              └─────────────┘                             │
       │         └──────────────────────────────────────────────────────────┘
       │                           │
       │                    ┌──────┴──────┐
       │                    │ PostgreSQL  │
       │                    │   :5435     │
       │                    └─────────────┘
       │                           ▲
       │                    ┌──────┴──────┐
       └────────────────────│ n8n (:5678) │
                            │ Automat.    │
                            └─────────────┘
                                   │
                           ┌───────┴───────┐
                           │  NVD API      │
                           │ (NIST CVE)    │
                           └───────────────┘
```

## Estructura del Proyecto

```
proyecto/
├── backend/
│   ├── app/
│   │   ├── main.py              # Entry point + middlewares
│   │   ├── database.py          # PostgreSQL + SQLAlchemy config
│   │   ├── models.py            # 6 entidades con Enums + índices
│   │   ├── schemas.py           # Pydantic v2 con validaciones
│   │   ├── auth.py              # JWT + refresh tokens + bcrypt
│   │   ├── seed.py              # Datos de prueba
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic Settings
│   │   │   ├── exceptions.py    # Exception handlers globales
│   │   │   ├── logging.py       # Logging con correlation ID
│   │   │   └── deps.py          # Dependencias (auth, roles)
│   │   ├── routers/             # 8 módulos de rutas REST
│   │   ├── services/            # 5 servicios de negocio
│   │   └── repositories/        # 5 repositorios de datos
│   ├── tests/                   # 30+ tests de integración
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Routing + estado global
│   │   ├── context/             # Autenticación con refresh tokens
│   │   ├── lib/api.ts           # Axios con interceptor JWT
│   │   ├── components/          # Layout, ProtectedRoute, UI
│   │   └── pages/               # 10 páginas
│   └── package.json
├── n8n_workflow.json            # Workflow de automatización
├── docker-compose.yml           # PostgreSQL + n8n + pgAdmin
├── .env.example                 # Variables de entorno
└── docs/
    ├── N8N_IMPLEMENTATION_SUMMARY.md
    └── N8N_WORKFLOW_GUIDE.md
```

## Requisitos

- Python 3.10+
- Node.js 18+
- Docker + Docker Compose
- npm

## Instalación y Ejecución

### 1. Base de Datos (PostgreSQL)

```bash
docker compose up postgres -d
```

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload
```

El backend estará en: `http://localhost:8000`
Documentación Swagger: `http://localhost:8000/docs`
Documentación Redoc: `http://localhost:8000/redoc`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

El frontend estará en: `http://localhost:5173`

### 4. n8n (Automatización)

```bash
docker compose up n8n -d
```

n8n estará en: `http://localhost:5678`

### 5. Todo junto

```bash
docker compose up -d
cd backend && uvicorn app.main:app --reload
cd frontend && npm run dev
```

## Credenciales de Prueba

| Usuario | Rol | Contraseña |
|---------|-----|-----------|
| admin | Administrador | Admin123! |
| analyst | Analista | Analyst123! |
| juan | Analista | Juan123! |
| maria | Analista (inactivo) | Maria123! |

## Endpoints de API

### Autenticación
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/login` | Login con JWT + refresh token |
| POST | `/auth/refresh` | Renovar access token |
| POST | `/auth/logout` | Revocar tokens |
| GET | `/auth/me` | Perfil del usuario actual |

### Vulnerabilidades
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/vulnerabilidades` | Listar (con paginación) |
| GET | `/vulnerabilidades/{id}` | Detalle |
| POST | `/vulnerabilidades` | Crear (admin) |
| PATCH | `/vulnerabilidades/{id}` | Actualizar (admin/analyst) |
| DELETE | `/vulnerabilidades/{id}` | Eliminar (admin) |

### Empresas, Usuarios, Comentarios, Estadísticas, Historial
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET/POST | `/empresas` | CRUD empresas |
| GET/POST/PATCH | `/usuarios` | CRUD usuarios (admin) |
| GET | `/comentarios` | Listar comentarios |
| POST | `/vulnerabilidades/{id}/comentarios` | Agregar comentario |
| GET | `/historial` | Auditoría de acciones |
| GET | `/estadisticas` | Dashboard stats |
| GET | `/estadisticas/tendencias` | Tendencias temporales |
| GET | `/health` | Health check (incluye DB) |

### n8n Webhooks
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/webhook/n8n/empresas` | Listar empresas para n8n |
| POST | `/webhook/n8n/vulnerabilidades` | Crear desde n8n |
| GET | `/webhook/n8n/vulnerabilidades/existe` | Idempotencia check |

## Testing

```bash
cd backend
.venv\Scripts\activate
pytest -v
```

## Funcionalidades Clave

- **Autenticación JWT con refresh token rotation**: Access tokens de 30 minutos, refresh tokens de 7 días con rotación y revocación
- **RBAC completo**: Roles admin, analyst y viewer con permisos granulares
- **Rate limiting**: Protección contra fuerza bruta en login (5 intentos / 15 min)
- **Logging con correlation ID**: Cada request tiene X-Request-ID único para trazabilidad
- **Exception handlers globales**: Respuestas de error consistentes con formato RFC 7807
- **Paginación**: Todos los listados con page/page_size
- **Enums con validación**: Severity, status, role validados en backend y DB
- **Auditoría completa**: HistoryLog con IP, actor, acción y timestamp
- **n8n con idempotencia**: No duplica vulnerabilidades existentes
- **EPSS realista**: Calculado desde CVSS con distribución estadística
- **Cálculo de IRC**: Fórmula propietaria CVSS×0.4 + EPSS×0.4 + AssetCrit×0.2

## Automatización n8n

El workflow de n8n:
1. Consulta la API de NVD (NIST) cada 3 horas
2. Extrae y normaliza campos (CVE, CVSS, descripción)
3. Calcula EPSS realista desde CVSS
4. Correlaciona con activos de la empresa
5. Calcula IRC (Índice de Riesgo Completo)
6. Verifica idempotencia (no duplicar CVEs existentes)
7. Asigna analista según severidad
8. Crea la vulnerabilidad en el backend
9. Genera resumen de ejecución

Ver `docs/N8N_IMPLEMENTATION_SUMMARY.md` y `docs/N8N_WORKFLOW_GUIDE.md` para detalles.

## Licencia

Proyecto académico — Grupo X (Saez & Kogan)
