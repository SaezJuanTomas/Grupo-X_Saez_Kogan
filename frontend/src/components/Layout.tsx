import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import type { SessionUser } from '../types'

type LayoutProps = {
  sessionUser: SessionUser
  onLogout: () => void
  children: ReactNode
}

const adminLinks = [
  { to: '/', label: 'Inicio' },
  { to: '/vulnerabilidades', label: 'Vulnerabilidades' },
  { to: '/empresas', label: 'Empresas' },
  { to: '/estadisticas', label: 'Estadísticas' },
  { to: '/equipo', label: 'Equipo' },
  { to: '/usuarios', label: 'Gestión de Usuarios' },
]

const analystLinks = [
  { to: '/', label: 'Inicio' },
  { to: '/vulnerabilidades', label: 'Vulnerabilidades' },
]

function NavItem({ to, label }: { to: string; label: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        [
          'rounded-xl px-3 py-2 text-sm font-medium transition',
          isActive ? 'bg-slate-900 text-white shadow-soft' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
        ].join(' ')
      }
    >
      {label}
    </NavLink>
  )
}

export function Layout({ sessionUser, onLogout, children }: LayoutProps) {
  const links = sessionUser.role === 'admin' ? adminLinks : analystLinks

  return (
    <div className="min-h-screen">
      <div className="flex min-h-screen">
        <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-slate-200 bg-white/90 px-4 py-5 backdrop-blur md:flex md:flex-col">
          <div className="mb-6 rounded-2xl bg-slate-950 px-4 py-4 text-white shadow-soft">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-300">Grupo X</p>
            <h1 className="mt-2 text-xl font-semibold">Cybersecurity MVP</h1>
            <p className="mt-2 text-sm text-slate-300">{sessionUser.role === 'admin' ? 'Vista administrativa' : 'Vista del analista'}</p>
          </div>

          <nav className="flex flex-1 flex-col gap-2">
            {links.map((link) => (
              <NavItem key={link.to} to={link.to} label={link.label} />
            ))}
          </nav>

          <button
            type="button"
            onClick={onLogout}
            className="mt-4 rounded-xl border border-slate-200 px-3 py-2 text-left text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
          >
            Cerrar sesión
          </button>
        </aside>

        <div className="flex min-h-screen flex-1 flex-col md:pl-64">
          <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/80 px-4 py-4 backdrop-blur md:px-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Seguridad interna</p>
                <h2 className="text-lg font-semibold text-slate-900 md:text-xl">Grupo X</h2>
              </div>
              <div className="flex items-center gap-3">
                <div className="hidden rounded-full bg-slate-100 px-3 py-2 text-sm text-slate-700 md:block">
                  {sessionUser.username} · {sessionUser.role}
                </div>
                <button
                  type="button"
                  onClick={onLogout}
                  className="rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-soft transition hover:bg-slate-700"
                >
                  Salir
                </button>
              </div>
            </div>
          </header>

          <main className="flex-1 px-4 py-6 md:px-6">{children}</main>
        </div>
      </div>
    </div>
  )
}
