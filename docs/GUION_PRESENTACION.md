# GUION DE PRESENTACION - Grupo X
## Plataforma de Gestion de Vulnerabilidades

> **Objetivo**: Vender la plataforma como solucion real, no explicar codigo.
> **Duracion sugerida**: 20-25 minutos + demo en vivo (10-15 min).

---

## PARTE 1 - APERTURA (2 min)

**[Slide: Titulo]**

> "Buenos dias. Hoy les vamos a presentar **Grupo X**, una plataforma de gestion y automatizacion de vulnerabilidades de seguridad informatica. No es un CRUD mas: es un sistema que recibe vulnerabilidades desde la fuente oficial de NIST, las enriquece automaticamente, las clasifica por riesgo y las pone en manos de los analistas listas para actuar."

**Mensaje clave**: No solo registramos vulnerabilidades. Las **detectamos, priorizamos y entregamos** al equipo listas para remediar.

---

## PARTE 2 - EL PROBLEMA QUE RESOLVEMOS (3 min)

**[Slide: El Problema]**

> "Las organizaciones hoy enfrentan un problema concreto: la cantidad de CVEs publicados crece exponencialmente. Solo en 2024 se publicaron mas de 32.000 vulnerabilidades en NVD. Los equipos de seguridad no pueden procesarlas manualmente."

**Tres dolores concretos:**

1. **Carga manual**: Un analista tiene que entrar a NVD, buscar CVEs relevantes, copiar datos, clasificarlos manualmente y recien ahi empezar a analizar. Esto toma horas por cada ciclo.

2. **Falta de priorizacion inteligente**: No todas las vulnerabilidades son igual de peligrosas. CVSS alone no dice si una vulnerabilidad esta siendo explotada activamente. Sin EPSS, el analista esta adivinando.

3. **Sin trazabilidad**: Quien detecto, cuando entro, que se hizo, que queda pendiente. En muchas organizaciones esto vive en mails y Excel.

> "Grupo X resuelve estos tres problemas con una plataforma integral que automatiza desde la deteccion hasta la gestion operativa."

---

## PARTE 3 - LA SOLUCION: VISION GENERAL (3 min)

**[Slide: Arquitectura de Alto Nivel]** (usar diagrama del README)

> "Nuestra plataforma tiene tres componentes principales que trabajan en conjunto:"

**1. Backend (FastAPI + PostgreSQL)**
> "El corazon del sistema. Una API REST con 27 endpoints que maneja autenticacion, autorizacion, CRUD completo, auditoria y estadisticas. Arquitectura en capas: Router, Service, Repository. Cada peticion pasa por autenticacion JWT, rate limiting y validacion."

**2. Frontend (React + TypeScript)**
> "Un panel de operacion donde los analistas y administradores trabajan. Dashboard con KPIs, listado de vulnerabilidades con filtros, detalle con comentarios e historial. La interfaz cambia segun el rol: un admin ve todo, un analista ve solo lo que le corresponde."

**3. Automatizacion (n8n)**
> "El diferenciador. Un workflow que corre cada 3 horas, consulta la API oficial de NIST, trae los CVEs mas recientes, los enriquece con datos de EPSS, los correlaciona con los activos de cada empresa y los carga automaticamente en la plataforma."

**Mensaje clave**: "La vulnerabilidad entra desde NIST, pasa por enriquecimiento automatico, queda almacenada, y aparece en el dashboard del analista. Todo sin intervencion manual."

---

## PARTE 4 - DEMO EN VIVO (10-15 min)

### 4.1 - Login y Dashboard (2 min)

**Acciones:**
1. Abrir `http://localhost:5173`
2. Loguearse como `admin` / `Admin123!`
3. Mostrar el Dashboard

**Que mostrar:**
> "Este es el dashboard. A la izquierda vemos los KPIs: vulnerabilidades criticas pendientes, total resueltas, usuarios activos. A la derecha, los ultimos casos asignados y la distribucion por severidad."

**Script:**
> "Todo lo que ven aca viene de la base de datos en tiempo real. No es hardcodeado."

### 4.2 - Vulnerabilidades (3 min)

**Acciones:**
1. Ir a "Vulnerabilidades"
2. Mostrar el listado con badges de severidad
3. Abrir una vulnerabilidad critica (ej: CVE con IRC alto)
4. Mostrar detalle, comentarios e historial

**Script:**
> "Cada vulnerabilidad viene con su CVE, severidad, estado y un indicador que se llama **IRC** - Indice de Riesgo Completo. No es solo CVSS: combina la severidad tecnica (CVSS), la probabilidad de explotacion real (EPSS) y la criticidad del activo afectado."

> "Al entrar al detalle, ven la trazabilidad completa: quien la creo, cuando cambio de estado, que analista esta asignado, y los comentarios del equipo. Todo queda registrado."

### 4.3 - Empresas y Correlacion (2 min)

**Acciones:**
1. Ir a "Empresas"
2. Mostrar una empresa con sus tecnologias
3. Explicar como n8n correlaciona

**Script:**
> "Cada empresa tiene un perfil de tecnologias: que bases de datos usa, que servidores, que frameworks. Cuando n8n trae un CVE nuevo, busca en la descripcion palabras clave que coincidan con las tecnologias de cada empresa, y asigna automaticamente la vulnerabilidad a la empresa correcta."

### 4.4 - Estadisticas (2 min)

**Acciones:**
1. Ir a "Estadisticas"
2. Mostrar graficos de severidad, tendencias y actividad de analistas

**Script:**
> "El modulo de estadisticas permite a los managers entender la postura de seguridad: que severidad predomina, como evoluciona en el tiempo, y que tan activos estan los analistas. Todo esto se genera automaticamente desde los datos operativos."

### 4.5 - Automatizacion n8n (3 min)

**Acciones:**
1. Abrir n8n en `http://localhost:5678`
2. Mostrar el workflow importado
3. Ejecutar manualmente (o mostrar el flujo grafico)

**Script:**
> "Este es el workflow de automatizacion. Tiene 18 nodos. Les muestro el flujo:"

1. **Consulta NVD** cada 3 horas
2. **Extrae** CVE, CVSS y descripcion
3. **Filtra** registros incompletos
4. **Normaliza** el CVSS y busca EPSS en FIRST.org
5. **Correlaciona** tecnologias con las empresas registradas
6. **Calcula el IRC** con nuestra formula propietaria
7. **Clasifica** criticidad (si IRC >= 7.5 es critico)
8. **Verifica** que no sea duplicado
9. **Inserta** en el backend automaticamente

> "Esto significa que cada 3 horas, la plataforma se actualiza sola con las ultimas vulnerabilidades relevantes para cada empresa del portafolio."

### 4.6 - Seguridad y Roles (1 min)

**Acciones:**
1. Cerrar sesion
2. Loguearse como `analyst` / `Analyst123!`
3. Mostrar que la navegacion cambia

**Script:**
> "Un analista no ve la gestion de usuarios ni puede crear vulnerabilidades. Solo ve lo que le asignaron. El sistema controla esto tanto en el backend como en el frontend. Ademas, cada login tiene rate limiting: despues de 5 intentos fallidos, se bloquea."

---

## PARTE 5 - DETALLES TECNICOS CLAVE (3 min)

**[Slide: Features]**

> "Algunos detalles que vale la pena destacar:"

### Seguridad
- **JWT con refresh token rotation**: Cada vez que se renueva el token, el anterior se invalida. Si alguien roba un token ya usado, no sirve.
- **Rate limiting**: Proteccion contra fuerza bruta en login.
- **RBAC**: Admin, Analyst, Viewer con permisos granulares.

### Automatizacion
- **EPSS real**: No adivinamos. Usamos los datos de FIRST.org (el consorcio de industria) que mide la probabilidad real de explotacion.
- **Idempotencia**: Si un CVE ya esta registrado, no se duplica. El workflow verifica antes de insertar.
- **Correlacion por activos**:匹配 las tecnologias de la empresa con la descripcion del CVE.
- **Trazabilidad de deteccion**: Medimos el tiempo entre la publicacion en NVD y nuestra insercion.

### Calidad
- **54 tests de integracion** pasando
- **Logging estructurado**: Cada request tiene un ID unico para trazabilidad.
- **Exception handlers globales**: Errores consistentes y predecibles.
- **Health check** con verificacion de base de datos.

### Notificaciones
- Cuando se asigna un CVE de alta criticidad a un analista, el sistema envia un email automatico (configurable via SMTP).

---

## PARTE 6 - CIERRE (2 min)

**[Slide: Resumen]**

> "Para cerrar: Grupo X no es un prototipo academico. Es una plataforma funcional que demuestra como la automatizacion puede transformar la gestion de vulnerabilidades."

**Lo que resuelve:**
- Reduce el tiempo de deteccion de horas a minutos
- Prioriza inteligentemente usando EPSS + CVSS + contexto del activo
- Da trazabilidad completa desde la fuente hasta la remediacion
- Escalable: agregar empresas, analistas o nuevas fuentes de datos

**El mensaje final:**
> "La seguridad informatica no se resuelve con mas personas. Se resuelve con mejores procesos automatizados. Grupo X es la prueba de que eso funciona."

---

## APPENDIX: ORDEN DE DEMO SUGERIDO

| Paso | Pantalla | Tiempo | Que mostrar |
|------|----------|--------|-------------|
| 1 | Login | 30s | Credenciales, rate limit |
| 2 | Dashboard | 2 min | KPIs, metricas en vivo |
| 3 | Vulnerabilidades | 3 min | Listado, badges, detalle |
| 4 | Empresa | 2 min | Tecnologias, correlacion |
| 5 | Estadisticas | 2 min | Graficos, tendencias |
| 6 | n8n | 3 min | Workflow, ejecucion |
| 7 | Roles | 1 min | Cambio de perspectiva |

---

## APPENDIX: PREGUNTAS FRECUENTES

**P: Por que EPSS en vez de solo CVSS?**
> R: CVSS mide la severidad tecnica. EPSS mide la probabilidad de que sea explotada en la practica. Combinarlos da una priorizacion mucho mas util.

**P: Que pasa si NVD cambia su API?**
> R: El workflow es modular. Si NVD cambia, solo se ajusta el nodo de extraccion. El resto del pipeline queda intacto.

**P: Esto escala?**
> R: Si. PostgreSQL maneja bien millones de registros. n8n puede distribuir carga. El backend usa paginacion en todos los listados.

**P: Como se despliega?**
> R: Docker Compose levanta todo. PostgreSQL, n8n y pgAdmin ya estan containerizados. Backend y frontend se pueden containerizar igual.

**P: Por que no usamos un framework de n8n ya hecho?**
> R: Porque necesitabamos control total sobre la correlacion, el IRC y la idempotencia. Un workflow custom da esa flexibilidad.

---

## APPENDIX: TECNOLOGIAS (para el slide final)

| Capa | Tecnologia |
|------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 |
| Base de Datos | PostgreSQL 16 |
| Frontend | React 18, TypeScript, Vite, TailwindCSS |
| Automatizacion | n8n 1.70 |
| Seguridad | JWT + refresh rotation, bcrypt, rate limiting |
| Testing | Pytest (54 tests), Vitest |
| Infraestructura | Docker Compose |

---

*Documento preparado para la presentacion del proyecto Grupo X - Tesis de Ingenieria*
*Saez & Kogan - 2026*
