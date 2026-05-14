import { Link } from 'react-router-dom'
import type { DashboardStats, Role, User, Vulnerability } from '../types'
import { Badge, Card, MetricCard, SectionTitle } from '../components/Ui'

type DashboardPageProps = {
  role: Role
  sessionUser: { id: number; username: string }
  vulnerabilities: Vulnerability[]
  users: User[]
  stats: DashboardStats
}

export function DashboardPage({ role, sessionUser, vulnerabilities, users, stats }: DashboardPageProps) {
  const assigned = vulnerabilities.filter((item) => item.assigned_analyst_id === sessionUser.id)
  const criticalAssigned = assigned.filter((item) => item.irc >= 8).length
  const pendingAssigned = assigned.filter((item) => item.status === 'Pendiente').length
  const criticalTotal = vulnerabilities.filter((item) => item.irc >= 8).length

  if (role === 'admin') {
    return (
      <div className="space-y-6">
        <div>
          <Badge tone="blue">Administrador</Badge>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">Bienvenido, {sessionUser.username}</h2>
          <p className="mt-2 max-w-2xl text-sm text-slate-500">Vista global del estado de seguridad, con métricas y accesos rápidos para presentar el caso de negocio de forma clara.</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <MetricCard label="Críticas" value={stats.critical} note="Vulnerabilidades con riesgo alto" />
          <MetricCard label="Pendientes" value={stats.pending} note="Requieren seguimiento" />
          <MetricCard label="Resueltas" value={stats.resolved} note="Casos cerrados" />
          <MetricCard label="Usuarios activos" value={stats.active_users} note="Cuentas habilitadas" />
        </div>

        <div className="grid gap-4 xl:grid-cols-3">
          <Card>
            <SectionTitle title="Accesos rápidos" subtitle="Atajos para operación diaria" />
            <div className="grid gap-3">
              <Link to="/vulnerabilidades" className="rounded-xl bg-slate-950 px-4 py-3 text-sm font-medium text-white hover:bg-slate-700">Ir a vulnerabilidades</Link>
              <Link to="/estadisticas" className="rounded-xl border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-50">Revisar estadísticas</Link>
              <Link to="/usuarios" className="rounded-xl border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-50">Gestionar usuarios</Link>
            </div>
          </Card>

          <Card>
            <SectionTitle title="Panorama del equipo" subtitle="Actividad resumida" />
            <div className="space-y-3 text-sm text-slate-600">
              {users.filter((user) => user.role === 'analyst').map((user) => (
                <div key={user.id} className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-3">
                  <div>
                    <p className="font-medium text-slate-900">{user.username}</p>
                    <p className="text-xs text-slate-500">{user.latest_activity}</p>
                  </div>
                  <Badge tone={user.active ? 'green' : 'red'}>{user.active ? 'Activo' : 'Inactivo'}</Badge>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <SectionTitle title="Casos críticos" subtitle="Listado de alto impacto" />
            <div className="space-y-3">
              {vulnerabilities.filter((item) => item.irc >= 8).slice(0, 3).map((item) => (
                <Link key={item.id} to={`/vulnerabilidades/${item.id}`} className="block rounded-xl border border-amber-200 bg-amber-50 p-3 transition hover:bg-amber-100">
                  <p className="text-sm font-semibold text-slate-900">{item.cve}</p>
                  <p className="mt-1 text-xs text-slate-600">{item.description}</p>
                </Link>
              ))}
              {criticalTotal === 0 ? <p className="text-sm text-slate-500">No hay casos críticos.</p> : null}
            </div>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <Badge tone="yellow">Analista</Badge>
        <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">Bienvenido, {sessionUser.username}</h2>
        <p className="mt-2 max-w-2xl text-sm text-slate-500">Tu vista está filtrada solo a vulnerabilidades asignadas, con foco en seguimiento operativo y actualización de estado.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <MetricCard label="Mis vulnerabilidades" value={assigned.length} note="Casos asignados" />
        <MetricCard label="Pendientes" value={pendingAssigned} note="Esperan acción" />
        <MetricCard label="Críticas asignadas" value={criticalAssigned} note="Requieren atención prioritaria" />
      </div>

      <Card>
        <SectionTitle title="Próximas acciones" subtitle="Resumen para la jornada" />
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {assigned.slice(0, 3).map((item) => (
            <Link key={item.id} to={`/vulnerabilidades/${item.id}`} className={`rounded-xl border p-4 transition hover:bg-slate-50 ${item.irc >= 8 ? 'border-amber-200 bg-amber-50' : 'border-slate-200 bg-white'}`}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-slate-900">{item.cve}</p>
                <Badge tone={item.irc >= 8 ? 'yellow' : 'slate'}>{item.status}</Badge>
              </div>
              <p className="mt-2 text-sm text-slate-600">{item.description}</p>
            </Link>
          ))}
          {assigned.length === 0 ? <p className="text-sm text-slate-500">No tienes vulnerabilidades asignadas.</p> : null}
        </div>
      </Card>
    </div>
  )
}
