# Backend - Sistema de Gestión de Vulnerabilidades

API REST construida con FastAPI para la gestión de vulnerabilidades de ciberseguridad.

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 2. Inicializar base de datos

```bash
python -m backend.seed
```

Esto creará:
- Base de datos SQLite (`vulnerabilities.db`)
- Usuarios de prueba
- Empresa de ejemplo
- Vulnerabilidades de muestra

### 3. Ejecutar servidor

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: http://localhost:8000

## 📚 Documentación API

Una vez ejecutado el servidor, visita: http://localhost:8000/docs

## 🔐 Autenticación

La API utiliza JWT tokens. Para autenticarte:

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@test.com&password=admin123"
```

## 📊 Endpoints Principales

### Vulnerabilidades
- `GET /vulnerabilidades/` - Listar vulnerabilidades
- `POST /vulnerabilidades/` - Crear vulnerabilidad
- `PUT /vulnerabilidades/{id}` - Actualizar vulnerabilidad
- `DELETE /vulnerabilidades/{id}` - Eliminar vulnerabilidad

### Usuarios
- `GET /usuarios/` - Listar usuarios (solo admin)
- `POST /usuarios/` - Crear usuario (solo admin)

### Comentarios
- `GET /comentarios/vulnerabilidad/{id}` - Comentarios de una vulnerabilidad
- `POST /comentarios/` - Agregar comentario

### Historial
- `GET /historial/vulnerabilidad/{id}` - Historial de una vulnerabilidad

## 🗄️ Base de Datos

- **Motor**: SQLite
- **Archivo**: `vulnerabilities.db`
- **ORM**: SQLAlchemy

## 🧪 Usuarios de Prueba

| Email | Contraseña | Rol |
|-------|------------|-----|
| admin@test.com | admin123 | Admin |
| analyst@test.com | analyst123 | Analyst |

## 🔧 Configuración

El archivo `config.py` contiene la configuración principal. Variables de entorno soportadas:

- `DATABASE_URL`: URL de conexión a la base de datos
- `SECRET_KEY`: Clave secreta para JWT
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Expiración de tokens

## 📁 Estructura del Proyecto

```
backend/
├── main.py              # Punto de entrada FastAPI
├── config.py            # Configuraciones
├── database.py          # Configuración SQLAlchemy
├── models.py            # Modelos de base de datos
├── seed.py              # Script de inicialización
├── requirements.txt     # Dependencias Python
└── routers/
    ├── auth.py          # Autenticación JWT
    ├── vulnerabilities.py # CRUD vulnerabilidades
    ├── users.py         # Gestión de usuarios
    ├── comments.py      # Comentarios
    └── history.py       # Historial de cambios
```