# Grupo X

MVP académico minimalista para un proyecto de tesis orientado a ciberseguridad. La idea es mostrar un flujo completo, profesional y fácil de explicar en una defensa: autenticación mock, tablero por rol, gestión de vulnerabilidades, comentarios, historial, estadísticas y una base preparada para integrar n8n más adelante.

## 1. Explicación del proyecto

Grupo X simula una herramienta interna para seguimiento de vulnerabilidades de seguridad. Un administrador puede ver todo el panorama, asignar analistas, crear usuarios, cambiar estados y revisar estadísticas. Un analista solo ve sus vulnerabilidades asignadas, comenta avances y actualiza estados.

El objetivo no es construir un sistema empresarial, sino un MVP claro, operativo y presentable. Por eso el proyecto prioriza:

- simplicidad antes que escalabilidad
- claridad antes que arquitectura compleja
- usabilidad antes que abstracciones innecesarias
- una demo realista que no falle si el backend no está levantado todavía

## 2. Tecnologías utilizadas

- Frontend: React, TypeScript, Vite, TailwindCSS
- Backend: FastAPI
- Base de datos: SQLite
- Estilo de navegación: sidebar fija + topbar + contenido dinámico

## 3. Estructura de carpetas

```text
Grupo X
├── backend
│   ├── app
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── seed.py
│   └── requirements.txt
├── frontend
│   ├── src
│   │   ├── components
│   │   ├── data
│   │   ├── pages
│   │   ├── lib
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── vite.config.ts
└── README.md
```

## 4. Instalación paso a paso

### Requisitos previos

- Node.js 18 o superior
- Python 3.10 o superior
- npm

### Paso 1: abrir dos terminales

Usa dos terminales separadas:

- Terminal 1: backend
- Terminal 2: frontend

### Paso 2: instalar dependencias del backend

```powershell
cd "c:\Programación\TESIS - Grupo X (Saez & Kogan)\backend"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Paso 3: instalar dependencias del frontend

```powershell
cd "c:\Programación\TESIS - Grupo X (Saez & Kogan)\frontend"
npm install
```

## 5. Comandos exactos para ejecutar

### Backend

```powershell
cd "c:\Programación\TESIS - Grupo X (Saez & Kogan)\backend"
.venv\Scripts\activate
uvicorn app.main:app --reload
```

### Frontend

```powershell
cd "c:\Programación\TESIS - Grupo X (Saez & Kogan)\frontend"
npm run dev
```

## 6. Cómo iniciar el frontend

1. Abre una terminal nueva.
2. Entra a la carpeta `frontend`.
3. Ejecuta `npm run dev`.
4. Abre la URL que muestra Vite, normalmente `http://localhost:5173`.

Si el backend no está corriendo, el frontend usa datos mock locales para seguir funcionando.

## 7. Cómo iniciar el backend

1. Abre una terminal nueva.
2. Entra a la carpeta `backend`.
3. Activa el entorno virtual.
4. Ejecuta `uvicorn app.main:app --reload`.

La API normalmente queda en `http://localhost:8000`.

## 8. Cómo inicializar la base de datos

La base SQLite se crea automáticamente al iniciar el backend por primera vez. No necesitas crear tablas manualmente.

En el primer arranque:

1. FastAPI crea el archivo SQLite.
2. Se generan las tablas.
3. Se cargan usuarios, compañías, vulnerabilidades, comentarios e historial de ejemplo.

Si borras la base, simplemente vuelve a iniciar el backend y se recreará.

## 9. Credenciales mock

### Administrador

- Usuario: `admin`
- Contraseña: `123`

### Analista

- Usuario: `analyst`
- Contraseña: `123`

## 10. Primer arranque, segundo arranque y arranques futuros

### Primer arranque

El primer arranque sirve para preparar todo el proyecto desde cero:

1. Instala dependencias del backend.
2. Instala dependencias del frontend.
3. Inicia el backend.
4. Inicia el frontend.
5. Abre la interfaz en el navegador.

### Segundo arranque

Si ya instalaste todo una vez y cerraste el proyecto, no repitas la instalación. Solo haz esto:

1. Abre Terminal 1.
2. Ve a `backend`.
3. Activa `.venv`.
4. Ejecuta `uvicorn app.main:app --reload`.
5. Abre Terminal 2.
6. Ve a `frontend`.
7. Ejecuta `npm run dev`.

### Arranques futuros

En los siguientes usos, normalmente solo necesitas repetir los comandos de ejecución. La base de datos SQLite conserva los datos entre reinicios, salvo que la elimines manualmente.

## 11. Flujo de uso recomendado

### Como administrador

1. Inicia sesión con `admin / 123`.
2. Revisa el inicio con métricas y accesos rápidos.
3. Entra a vulnerabilidades para crear o editar casos.
4. Revisa estadísticas.
5. Gestiona equipo y usuarios.

### Como analista

1. Inicia sesión con `analyst / 123`.
2. Consulta únicamente las vulnerabilidades asignadas.
3. Agrega comentarios.
4. Cambia estados cuando corresponda.

## 12. Endpoints principales del backend

- `GET /health`
- `GET /estadisticas`
- `GET /vulnerabilidades`
- `POST /vulnerabilidades`
- `GET /vulnerabilidades/{id}`
- `PATCH /vulnerabilidades/{id}`
- `GET /usuarios`
- `POST /usuarios`
- `PATCH /usuarios/{id}`
- `POST /vulnerabilidades/{id}/comentarios`
- `GET /historial`

## 13. Integración futura con n8n

El proyecto ya deja la estructura de endpoints lista para integraciones futuras con n8n sin rehacer el backend.

Casos de uso futuros:

- crear vulnerabilidades automáticamente desde formularios o alertas externas
- actualizar estados desde flujos automáticos
- disparar alertas cuando una vulnerabilidad crítica cambie de estado
- sincronizar comentarios o eventos de historial

La idea es que n8n pueda consumir la API con endpoints simples como `POST /vulnerabilidades` o `PATCH /vulnerabilidades/{id}` y automatizar procesos sin modificar demasiado el núcleo del sistema.

## 14. Troubleshooting común

### El frontend no carga datos

- Verifica que el backend esté encendido en `http://localhost:8000`.
- Si no lo está, el frontend igualmente usa datos mock, así que la interfaz debería seguir operativa.

### El backend no arranca

- Revisa que el entorno virtual esté activado.
- Confirma que instalaste `requirements.txt`.
- Verifica que no haya otro proceso usando el puerto `8000`.

### El navegador muestra una pantalla vacía

- Revisa la consola del navegador.
- Confirma que el archivo `.env` no esté apuntando a una URL incorrecta.
- Si borraste datos, vuelve a iniciar el backend para regenerar la base.

### No encuentro la base SQLite

- La base se crea automáticamente dentro de `backend/app/` como `grupo_x.db`.
- Si no existe, inicia el backend una vez.

## 15. Nota para la defensa de tesis

Este MVP está pensado para explicarse de forma simple:

- un login mock define el rol
- el layout cambia según el rol
- la base SQLite guarda la información
- el backend expone CRUD simple
- la interfaz siempre tiene fallback para no romper la demo
- la arquitectura ya permite evolucionar luego hacia automatización con n8n
