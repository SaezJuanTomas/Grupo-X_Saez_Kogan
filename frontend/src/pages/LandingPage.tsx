import { useState, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export const SYSTEM_NAME = 'Plataforma IRC'
export const SYSTEM_TAGLINE = 'Gestión y priorización automatizada de vulnerabilidades'

type LandingPageProps = {
  onLogout?: () => void
}

const navLinks = [
  { href: '#problema', label: 'Problema' },
  { href: '#solucion', label: 'Solución' },
  { href: '#funcionalidades', label: 'Funcionalidades' },
  { href: '#validacion', label: 'Validación' },
  { href: '#como-funciona', label: 'Cómo funciona' },
  { href: '#roles', label: 'Roles' },
]

function roleLabel(role: string): string {
  if (role === 'admin') return 'Administrador'
  if (role === 'analyst') return 'Analista'
  return role
}

const icons = {
  shield: <path d="M12 22s8-3.5 8-10V5l-8-3-8 3v7c0 6.5 8 10 8 10z" />,
  inbox: (
    <>
      <polyline points="22 12 16 12 14 15 10 15 8 12 2 12" />
      <path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z" />
    </>
  ),
  sliders: (
    <>
      <line x1="21" x2="14" y1="4" y2="4" />
      <line x1="10" x2="3" y1="4" y2="4" />
      <line x1="21" x2="12" y1="12" y2="12" />
      <line x1="8" x2="3" y1="12" y2="12" />
      <line x1="21" x2="16" y1="20" y2="20" />
      <line x1="12" x2="3" y1="20" y2="20" />
      <line x1="14" x2="14" y1="2" y2="6" />
      <line x1="8" x2="8" y1="10" y2="14" />
      <line x1="16" x2="16" y1="18" y2="22" />
    </>
  ),
  timer: (
    <>
      <line x1="10" x2="14" y1="2" y2="2" />
      <line x1="12" x2="15" y1="14" y2="11" />
      <circle cx="12" cy="14" r="8" />
    </>
  ),
  wallet: (
    <>
      <rect width="20" height="14" x="2" y="5" rx="2" />
      <line x1="2" x2="22" y1="10" y2="10" />
    </>
  ),
  zap: <path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z" />,
  database: (
    <>
      <ellipse cx="12" cy="5" rx="8" ry="3" />
      <path d="M4 5v14c0 1.66 3.58 3 8 3s8-1.34 8-3V5" />
      <path d="M4 12c0 1.66 3.58 3 8 3s8-1.34 8-3" />
    </>
  ),
  network: (
    <>
      <circle cx="12" cy="5" r="2.5" />
      <circle cx="5" cy="19" r="2.5" />
      <circle cx="19" cy="19" r="2.5" />
      <path d="M12 7.5v4M12 11.5 6.4 17M12 11.5l5.6 5.5" />
    </>
  ),
  gauge: (
    <>
      <path d="m12 14 4-4" />
      <path d="M3.34 19a10 10 0 1 1 17.32 0" />
    </>
  ),
  users: (
    <>
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </>
  ),
  message: <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />,
  layout: (
    <>
      <rect width="7" height="9" x="3" y="3" rx="1" />
      <rect width="7" height="5" x="14" y="3" rx="1" />
      <rect width="7" height="9" x="14" y="12" rx="1" />
      <rect width="7" height="5" x="3" y="16" rx="1" />
    </>
  ),
  history: (
    <>
      <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
      <path d="M3 3v5h5" />
      <path d="M12 7v5l4 2" />
    </>
  ),
  lock: (
    <>
      <rect width="18" height="11" x="3" y="11" rx="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </>
  ),
  search: (
    <>
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.3-4.3" />
    </>
  ),
  bell: (
    <>
      <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
      <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
    </>
  ),
  clipboard: (
    <>
      <rect width="8" height="4" x="8" y="2" rx="1" />
      <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
      <path d="M12 11h4" />
      <path d="M12 16h4" />
      <path d="M8 11h.01" />
      <path d="M8 16h.01" />
    </>
  ),
  check: <path d="M20 6 9 17l-5-5" />,
  arrowRight: (
    <>
      <path d="M5 12h14" />
      <path d="m12 5 7 7-7 7" />
    </>
  ),
} satisfies Record<string, ReactNode>

type IconName = keyof typeof icons

function Icon({ name, className = 'h-5 w-5' }: { name: IconName; className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {icons[name]}
    </svg>
  )
}

function BrandMark({ className = 'h-9 w-9' }: { className?: string }) {
  return (
    <span className={`flex items-center justify-center rounded-xl bg-slate-950 text-white shadow-soft ${className}`}>
      <Icon name="shield" className="h-5 w-5" />
    </span>
  )
}

const problemItems = [
  {
    icon: 'inbox' as IconName,
    title: 'Cobertura incompleta',
    text: 'El volumen diario de vulnerabilidades publicadas en la NVD supera la capacidad de revisión manual de un equipo chico: vulnerabilidades relevantes pasan desapercibidas.',
  },
  {
    icon: 'sliders' as IconName,
    title: 'Priorización subóptima',
    text: '"Qué arreglar primero" se decide casi siempre por el puntaje CVSS, sin considerar la probabilidad real de explotación (EPSS) ni la importancia del activo para el negocio.',
  },
  {
    icon: 'timer' as IconName,
    title: 'Latencia y falta de trazabilidad',
    text: 'Boletines, planillas y chats informales generan ventanas de exposición largas y sin registro sistemático del estado de cada vulnerabilidad.',
  },
  {
    icon: 'wallet' as IconName,
    title: 'Licenciamiento prohibitivo',
    text: 'Las plataformas SOAR comerciales que resuelven este problema tienen costos de licencia fuera del alcance de equipos medianos.',
  },
]

const pipelineSteps = [
  { label: 'Detección', text: 'Consulta periódica de las APIs oficiales de NVD (NIST) y EPSS (FIRST).' },
  { label: 'Correlación', text: 'Cada CVE se cruza con las tecnologías declaradas por cada empresa del inventario.' },
  { label: 'Priorización', text: 'Se calcula el IRC combinando severidad, explotabilidad y criticidad del activo.' },
  { label: 'Notificación', text: 'La vulnerabilidad queda asignada y visible con su nivel de urgencia real.' },
  { label: 'Seguimiento', text: 'Estados, comentarios e historial auditable durante toda la remediación.' },
]

const features = [
  {
    icon: 'zap' as IconName,
    title: 'Ingesta automática de CVEs',
    text: 'Pipeline que consulta la NVD y el FIRST (EPSS) periódicamente y crea las vulnerabilidades sin intervención manual.',
  },
  {
    icon: 'database' as IconName,
    title: 'Inventario de vulnerabilidades',
    text: 'Alta, baja, consulta y edición por CVE, con severidad, estado de remediación, empresa afectada e IRC calculado.',
  },
  {
    icon: 'network' as IconName,
    title: 'Correlación con activos',
    text: 'Matching automático entre las tecnologías declaradas por cada empresa y la descripción de cada CVE.',
  },
  {
    icon: 'gauge' as IconName,
    title: 'Priorización mediante IRC',
    text: 'Índice de Riesgo Compuesto: severidad técnica, probabilidad de explotación y criticidad del negocio, no solo CVSS.',
  },
  {
    icon: 'users' as IconName,
    title: 'Roles y permisos',
    text: 'Permisos diferenciados por rol aplicados tanto en frontend como en backend, no solo cosméticos.',
  },
  {
    icon: 'message' as IconName,
    title: 'Seguimiento colaborativo',
    text: 'Comentarios por vulnerabilidad y coordinación del ciclo de remediación en equipo.',
  },
  {
    icon: 'layout' as IconName,
    title: 'Dashboards por rol',
    text: 'Métricas por severidad, estado, rango de IRC y evolución temporal. Cada usuario ve solo lo que le corresponde.',
  },
  {
    icon: 'history' as IconName,
    title: 'Historial auditable',
    text: 'Registro automático e inmutable de creación, asignación, cambios de estado y comentarios, con timestamp.',
  },
  {
    icon: 'lock' as IconName,
    title: 'Autenticación segura',
    text: 'JWT con refresh tokens, contraseñas hasheadas con bcrypt y revocación de sesión.',
  },
]

const validationMetrics = [
  { value: '32/32', label: 'Requisitos funcionales del MVP', note: 'Implementados y verificados en sesiones de demostración controladas.' },
  { value: '27', label: 'Endpoints REST', note: 'Distribuidos en 8 routers del backend.' },
  { value: '18', label: 'Nodos de automatización', note: 'Pipeline completo de ingesta, correlación y cálculo de IRC.' },
  { value: '~8 s', label: '5 CVEs reales procesados', note: 'Medido en una corrida de demostración del pipeline.' },
  { value: '100', label: 'CVEs reales validados', note: 'Con NVD + EPSS real vía API del FIRST (jul–ago 2026).' },
  { value: '3,96/10', label: 'IRC medio de la muestra', note: 'Mediana: 4,11 sobre los 100 CVEs evaluados.' },
  { value: '50/100', label: 'Casos donde el IRC reordenó la prioridad', note: 'Frente al CVSS puro; la otra mitad coincidió con su banda de severidad.' },
  { value: 'r = 0,953', label: 'Correlación IRC–CVSS', note: 'Coeficiente de Pearson sobre la muestra validada.' },
]

const howItWorks = [
  { title: 'Consulta NVD / EPSS', text: 'El sistema consulta automáticamente la base pública de vulnerabilidades (NVD) y el puntaje de probabilidad de explotación (EPSS) del FIRST.' },
  { title: 'Detecta nuevas vulnerabilidades', text: 'Las publicaciones nuevas se incorporan al inventario sin revisión manual de boletines.' },
  { title: 'Correlaciona con activos', text: 'Cada CVE se cruza con el inventario de tecnologías declaradas por tus empresas y activos registrados.' },
  { title: 'Calcula el IRC', text: 'Severidad técnica (40%) + probabilidad de explotación (40%) + criticidad del activo para el negocio (20%).' },
  { title: 'El analista gestiona desde su dashboard', text: 'La vulnerabilidad queda asignada a la empresa, visible con su urgencia real, lista para gestionar estado, comentarios y seguimiento auditable.' },
]

const differentials = [
  'Automatiza las tres etapas que más tiempo consumen en un proceso manual: detección, correlación con inventario y cálculo de prioridad.',
  'Prioriza con contexto real del negocio, evitando gastar recursos escasos en riesgos de bajo impacto real.',
  'Deja trazabilidad automática de todo el ciclo de vida de cada vulnerabilidad.',
  'Construido enteramente con herramientas open source.',
  'Sin costo de licenciamiento de plataforma SOAR comercial.',
  'Pesos del IRC configurables, adaptables a los criterios de cada organización.',
]

const rolesCards = [
  {
    icon: 'shield' as IconName,
    name: 'Administrador',
    tone: 'border-slate-200',
    items: ['Gestión completa del sistema', 'Empresas, usuarios y equipo', 'Estadísticas globales'],
  },
  {
    icon: 'clipboard' as IconName,
    name: 'Analista',
    tone: 'border-slate-200',
    items: ['Vulnerabilidades asignadas', 'Actualización de estados', 'Comentarios y seguimiento'],
  },
]

export function LandingPage({ onLogout }: LandingPageProps) {
  const { user } = useAuth()
  const [menuOpen, setMenuOpen] = useState(false)

  function closeMenu() {
    setMenuOpen(false)
  }

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 md:px-6">
          <Link to="/" className="flex items-center gap-3" aria-label={`${SYSTEM_NAME} — inicio`}>
            <BrandMark />
            <span>
              <span className="block text-sm font-semibold tracking-tight text-slate-900">{SYSTEM_NAME}</span>
              <span className="hidden text-xs text-slate-500 sm:block">{SYSTEM_TAGLINE}</span>
            </span>
          </Link>

          <nav className="hidden items-center gap-1 lg:flex" aria-label="Navegación de la landing">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="rounded-xl px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
              >
                {link.label}
              </a>
            ))}
          </nav>

          <div className="hidden items-center gap-3 md:flex">
            {user ? (
              <>
                <span className="rounded-full bg-slate-100 px-3 py-2 text-sm text-slate-700">
                  {user.username} · {roleLabel(user.role)}
                </span>
                <Link
                  to="/inicio"
                  className="rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-soft transition hover:bg-slate-700"
                >
                  Ir a mi dashboard
                </Link>
                {onLogout ? (
                  <button
                    type="button"
                    onClick={onLogout}
                    className="rounded-full border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
                  >
                    Salir
                  </button>
                ) : null}
              </>
            ) : (
              <Link
                to="/login"
                className="rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-soft transition hover:bg-slate-700"
              >
                Iniciar sesión
              </Link>
            )}
          </div>

          <button
            type="button"
            onClick={() => setMenuOpen((open) => !open)}
            aria-expanded={menuOpen}
            aria-label={menuOpen ? 'Cerrar menú' : 'Abrir menú'}
            className="rounded-xl border border-slate-200 p-2 text-slate-700 transition hover:bg-slate-50 md:hidden"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" className="h-5 w-5" aria-hidden="true">
              {menuOpen ? (
                <>
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </>
              ) : (
                <>
                  <line x1="4" y1="6" x2="20" y2="6" />
                  <line x1="4" y1="12" x2="20" y2="12" />
                  <line x1="4" y1="18" x2="20" y2="18" />
                </>
              )}
            </svg>
          </button>
        </div>

        {menuOpen ? (
          <div className="border-t border-slate-200 bg-white px-4 py-4 md:hidden">
            <nav className="grid gap-1" aria-label="Navegación móvil">
              {navLinks.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={closeMenu}
                  className="rounded-xl px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
                >
                  {link.label}
                </a>
              ))}
            </nav>
            <div className="mt-4 grid gap-2">
              {user ? (
                <>
                  <Link
                    to="/inicio"
                    onClick={closeMenu}
                    className="rounded-xl bg-slate-950 px-4 py-3 text-center text-sm font-medium text-white transition hover:bg-slate-700"
                  >
                    Ir a mi dashboard ({user.username})
                  </Link>
                  {onLogout ? (
                    <button
                      type="button"
                      onClick={() => { closeMenu(); onLogout() }}
                      className="rounded-xl border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
                    >
                      Salir
                    </button>
                  ) : null}
                </>
              ) : (
                <Link
                  to="/login"
                  onClick={closeMenu}
                  className="rounded-xl bg-slate-950 px-4 py-3 text-center text-sm font-medium text-white transition hover:bg-slate-700"
                >
                  Iniciar sesión
                </Link>
              )}
            </div>
          </div>
        ) : null}
      </header>

      <main>
        <section id="inicio" className="mx-auto max-w-6xl px-4 pb-16 pt-12 md:px-6 md:pb-24 md:pt-20">
          <div className="grid items-center gap-10 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="animate-fade-up">
              <p className="inline-flex flex-wrap items-center gap-x-2 rounded-full border border-slate-200 bg-white/80 px-4 py-1.5 text-xs font-semibold text-slate-600 shadow-soft">
                <span>100% código abierto</span>
                <span aria-hidden="true">·</span>
                <span>Sin costo de licenciamiento</span>
                <span aria-hidden="true">·</span>
                <span>Pensado para PyMEs tecnológicas</span>
              </p>
              <h1 className="mt-6 text-4xl font-semibold leading-tight tracking-tight text-slate-900 md:text-5xl">
                Detectá, priorizá y gestioná vulnerabilidades de seguridad automáticamente —{' '}
                <span className="text-slate-500">sin pagar licencias de plataformas SOAR.</span>
              </h1>
              <p className="mt-5 max-w-2xl text-base leading-7 text-slate-600 md:text-lg">
                Plataforma web open source que combina <strong className="font-semibold text-slate-800">CVSS + EPSS + criticidad de negocio</strong> en
                un solo índice de riesgo (<strong className="font-semibold text-slate-800">IRC</strong>), para que sepas qué vulnerabilidad atender primero.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                {user ? (
                  <Link
                    to="/inicio"
                    className="inline-flex items-center gap-2 rounded-xl bg-slate-950 px-5 py-3 text-sm font-medium text-white shadow-soft transition hover:bg-slate-700"
                  >
                    Ir a mi dashboard
                    <Icon name="arrowRight" className="h-4 w-4" />
                  </Link>
                ) : (
                  <Link
                    to="/login"
                    className="inline-flex items-center gap-2 rounded-xl bg-slate-950 px-5 py-3 text-sm font-medium text-white shadow-soft transition hover:bg-slate-700"
                  >
                    Explorar el sistema
                    <Icon name="arrowRight" className="h-4 w-4" />
                  </Link>
                )}
                <a
                  href="#como-funciona"
                  className="inline-flex items-center rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
                >
                  Conocer cómo funciona
                </a>
              </div>
            </div>

            <div className="animate-fade-up [animation-delay:150ms]">
              <div className="rounded-[2rem] border border-slate-200 bg-slate-950 p-6 text-white shadow-soft md:p-8">
                <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Índice de Riesgo Compuesto</p>
                <p className="mt-4 text-lg font-semibold leading-snug">
                  IRC = <span className="text-sky-300">CVSS × 40%</span> + <span className="text-emerald-300">EPSS × 40%</span> +{' '}
                  <span className="text-amber-300">Criticidad del activo × 20%</span>
                </p>
                <div className="mt-6 space-y-4">
                  <div>
                    <div className="flex items-center justify-between text-xs text-slate-300">
                      <span>Severidad técnica (CVSS)</span>
                      <span>40%</span>
                    </div>
                    <div className="mt-1.5 h-2 rounded-full bg-white/10">
                      <div className="h-2 w-2/5 rounded-full bg-sky-400" />
                    </div>
                  </div>
                  <div>
                    <div className="flex items-center justify-between text-xs text-slate-300">
                      <span>Probabilidad de explotación (EPSS)</span>
                      <span>40%</span>
                    </div>
                    <div className="mt-1.5 h-2 rounded-full bg-white/10">
                      <div className="h-2 w-2/5 rounded-full bg-emerald-400" />
                    </div>
                  </div>
                  <div>
                    <div className="flex items-center justify-between text-xs text-slate-300">
                      <span>Criticidad del activo para el negocio</span>
                      <span>20%</span>
                    </div>
                    <div className="mt-1.5 h-2 rounded-full bg-white/10">
                      <div className="h-2 w-1/5 rounded-full bg-amber-400" />
                    </div>
                  </div>
                </div>
                <div className="mt-6 grid grid-cols-3 gap-2 text-center text-xs text-slate-300">
                  <div className="rounded-xl border border-white/10 bg-white/5 px-2 py-3">NVD<br />(NIST)</div>
                  <div className="rounded-xl border border-white/10 bg-white/5 px-2 py-3">EPSS<br />(FIRST)</div>
                  <div className="rounded-xl border border-white/10 bg-white/5 px-2 py-3">Inventario<br />de activos</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="problema" className="scroll-mt-20 border-t border-slate-200 bg-white/60 py-16 md:py-24">
          <div className="mx-auto max-w-6xl px-4 md:px-6">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">El problema</p>
            <h2 className="mt-3 max-w-3xl text-3xl font-semibold tracking-tight text-slate-900 md:text-4xl">
              Revisar boletines a mano no escala para equipos de 1 a 3 personas
            </h2>
            <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600">
              Los equipos de seguridad en empresas medianas suelen tener entre 1 y 3 personas cubriendo múltiples responsabilidades a la vez.
              El proceso manual no alcanza.
            </p>
            <div className="mt-10 grid gap-4 sm:grid-cols-2">
              {problemItems.map((item) => (
                <article key={item.title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft transition hover:-translate-y-0.5 hover:shadow-lg">
                  <span className="inline-flex rounded-xl bg-slate-100 p-2.5 text-slate-700">
                    <Icon name={item.icon} />
                  </span>
                  <h3 className="mt-4 text-lg font-semibold text-slate-900">{item.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{item.text}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="solucion" className="scroll-mt-20 py-16 md:py-24">
          <div className="mx-auto max-w-6xl px-4 md:px-6">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">La solución</p>
            <h2 className="mt-3 max-w-3xl text-3xl font-semibold tracking-tight text-slate-900 md:text-4xl">
              Un ciclo automatizado, de la publicación del CVE hasta la remediación
            </h2>
            <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600">
              Una plataforma web —no solo un script— que automatiza el ciclo completo usando fuentes oficiales (NVD + EPSS),
              el inventario de activos y un índice de riesgo propio.
            </p>

            <ol className="mt-10 grid gap-4 md:grid-cols-5">
              {pipelineSteps.map((step, index) => (
                <li key={step.label} className="relative rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
                  <span className="text-xs font-semibold uppercase tracking-widest text-slate-400">Paso {index + 1}</span>
                  <h3 className="mt-2 text-base font-semibold text-slate-900">{step.label}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{step.text}</p>
                  {index < pipelineSteps.length - 1 ? (
                    <span className="absolute -right-3 top-1/2 hidden -translate-y-1/2 text-slate-300 md:block" aria-hidden="true">
                      <Icon name="arrowRight" className="h-4 w-4" />
                    </span>
                  ) : null}
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section id="funcionalidades" className="scroll-mt-20 border-y border-slate-200 bg-white/60 py-16 md:py-24">
          <div className="mx-auto max-w-6xl px-4 md:px-6">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Funcionalidades</p>
            <h2 className="mt-3 max-w-3xl text-3xl font-semibold tracking-tight text-slate-900 md:text-4xl">
              Todo lo que el sistema hace hoy, implementado
            </h2>
            <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {features.map((feature) => (
                <article key={feature.title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft transition hover:-translate-y-0.5 hover:shadow-lg">
                  <span className="inline-flex rounded-xl bg-slate-950 p-2.5 text-white">
                    <Icon name={feature.icon} />
                  </span>
                  <h3 className="mt-4 text-lg font-semibold text-slate-900">{feature.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{feature.text}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="validacion" className="scroll-mt-20 py-16 md:py-24">
          <div className="mx-auto max-w-6xl px-4 md:px-6">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Evidencia</p>
            <h2 className="mt-3 max-w-3xl text-3xl font-semibold tracking-tight text-slate-900 md:text-4xl">
              Resultados de la validación del prototipo
            </h2>
            <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600">
              Cifras obtenidas en la validación experimental del proyecto y en sesiones de demostración
              controladas (jul–ago 2026).
            </p>
            <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {validationMetrics.map((metric) => (
                <article key={metric.label} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
                  <p className="text-3xl font-semibold tracking-tight text-slate-900">{metric.value}</p>
                  <p className="mt-2 text-sm font-medium text-slate-700">{metric.label}</p>
                  <p className="mt-1 text-xs leading-5 text-slate-500">{metric.note}</p>
                </article>
              ))}
            </div>
            <div className="mt-8 rounded-2xl border border-slate-200 bg-slate-50 p-5 text-sm leading-6 text-slate-600">
              El IRC incorpora al cálculo la explotabilidad (EPSS) y la criticidad de negocio de cada activo:
              la prioridad refleja el contexto real de cada organización, no solo un puntaje técnico genérico.
            </div>
          </div>
        </section>

        <section id="como-funciona" className="scroll-mt-20 border-y border-slate-200 bg-slate-950 py-16 text-white md:py-24">
          <div className="mx-auto max-w-6xl px-4 md:px-6">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Cómo funciona</p>
            <h2 className="mt-3 max-w-3xl text-3xl font-semibold tracking-tight md:text-4xl">
              Cinco pasos, cero revisión manual de boletines
            </h2>
            <ol className="mt-10 space-y-4">
              {howItWorks.map((step, index) => (
                <li key={step.title} className="flex gap-4 rounded-2xl border border-white/10 bg-white/5 p-5 md:p-6">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white text-base font-semibold text-slate-950">
                    {index + 1}
                  </span>
                  <div>
                    <h3 className="text-base font-semibold md:text-lg">{step.title}</h3>
                    <p className="mt-1 text-sm leading-6 text-slate-300">{step.text}</p>
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section id="diferencial" className="scroll-mt-20 py-16 md:py-24">
          <div className="mx-auto grid max-w-6xl gap-10 px-4 md:px-6 lg:grid-cols-[0.9fr_1.1fr]">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-slate-500">El diferencial</p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900 md:text-4xl">
                Automatización con contexto, trazabilidad y costo cero de licencias
              </h2>
              <p className="mt-4 text-base leading-7 text-slate-600">
                Un caso de uso específico —detección, priorización y notificación— resuelto con herramientas abiertas,
                no un intento de reemplazar una suite SOAR completa.
              </p>
            </div>
            <ul className="space-y-3">
              {differentials.map((item) => (
                <li key={item} className="flex items-start gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-soft">
                  <span className="mt-0.5 inline-flex rounded-full bg-emerald-100 p-1 text-emerald-700">
                    <Icon name="check" className="h-3.5 w-3.5" />
                  </span>
                  <p className="text-sm leading-6 text-slate-700">{item}</p>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section id="roles" className="scroll-mt-20 border-t border-slate-200 bg-white/60 py-16 md:py-24">
          <div className="mx-auto max-w-6xl px-4 md:px-6">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Roles</p>
            <h2 className="mt-3 max-w-3xl text-3xl font-semibold tracking-tight text-slate-900 md:text-4xl">
              Cada rol ve solo lo que le corresponde
            </h2>
            <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600">
              Permisos reales aplicados en frontend y backend, para que el trabajo en equipo quede ordenado.
            </p>
            <div className="mt-10 grid gap-4 md:grid-cols-2">
              {rolesCards.map((card) => (
                <article key={card.name} className={`rounded-2xl border ${card.tone} bg-white p-6 shadow-soft`}>
                  <span className="inline-flex rounded-xl bg-slate-100 p-2.5 text-slate-700">
                    <Icon name={card.icon} />
                  </span>
                  <h3 className="mt-4 text-lg font-semibold text-slate-900">{card.name}</h3>
                  <ul className="mt-3 space-y-2">
                    {card.items.map((item) => (
                      <li key={item} className="flex items-start gap-2 text-sm text-slate-600">
                        <span className="mt-1 text-slate-400" aria-hidden="true">
                          <Icon name="check" className="h-3.5 w-3.5" />
                        </span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </article>
              ))}
            </div>
            <div className="mt-8">
              <Link
                to="/login"
                className="inline-flex items-center gap-2 rounded-xl bg-slate-950 px-5 py-3 text-sm font-medium text-white shadow-soft transition hover:bg-slate-700"
              >
                Acceder al sistema
                <Icon name="arrowRight" className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 py-16 md:px-6 md:py-24">
          <div className="rounded-[2rem] border border-slate-200 bg-slate-950 p-8 text-center text-white shadow-soft md:p-14">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Prototipo académico validado</p>
            <h2 className="mx-auto mt-4 max-w-2xl text-3xl font-semibold tracking-tight md:text-4xl">
              Conocé la plataforma por dentro
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-sm leading-7 text-slate-300 md:text-base">
              El sistema está validado funcionalmente y en desarrollo activo. Ingresá con tu usuario para explorar el
              inventario de vulnerabilidades, el cálculo de IRC y los dashboards por rol.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-3">
              {user ? (
                <Link
                  to="/inicio"
                  className="inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3 text-sm font-medium text-slate-950 transition hover:bg-slate-200"
                >
                  Ir a mi dashboard
                  <Icon name="arrowRight" className="h-4 w-4" />
                </Link>
              ) : (
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3 text-sm font-medium text-slate-950 transition hover:bg-slate-200"
                >
                  Iniciar sesión
                  <Icon name="arrowRight" className="h-4 w-4" />
                </Link>
              )}
              <a
                href="#como-funciona"
                className="inline-flex items-center rounded-xl border border-white/20 px-6 py-3 text-sm font-medium text-white transition hover:bg-white/10"
              >
                Ver cómo funciona
              </a>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-200 bg-white/70">
        <div className="mx-auto max-w-6xl px-4 py-10 md:px-6">
          <div className="flex flex-col gap-8 md:flex-row md:items-start md:justify-between">
            <div className="max-w-sm">
              <div className="flex items-center gap-3">
                <BrandMark />
                <span>
                  <span className="block text-sm font-semibold text-slate-900">{SYSTEM_NAME}</span>
                  <span className="block text-xs text-slate-500">{SYSTEM_TAGLINE}</span>
                </span>
              </div>
              <p className="mt-4 text-xs leading-5 text-slate-500">
                Proyecto académico (UTN FRM, 2026): notificación automatizada de vulnerabilidades hacia la reducción de
                ventanas de exposición. Prototipo open source validado funcionalmente.
              </p>
            </div>
            <nav className="grid grid-cols-2 gap-x-10 gap-y-2 text-sm text-slate-600" aria-label="Navegación del pie de página">
              {navLinks.map((link) => (
                <a key={link.href} href={link.href} className="transition hover:text-slate-900">
                  {link.label}
                </a>
              ))}
              <Link to="/login" className="transition hover:text-slate-900">
                Iniciar sesión
              </Link>
            </nav>
          </div>
          <div className="mt-8 border-t border-slate-200 pt-6 text-xs text-slate-500">
            {SYSTEM_NAME} — código abierto, sin costo de licenciamiento.
          </div>
        </div>
      </footer>
    </div>
  )
}
