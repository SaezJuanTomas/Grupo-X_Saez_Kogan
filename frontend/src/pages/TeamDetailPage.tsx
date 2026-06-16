import { Link, useParams } from 'react-router-dom'
import type { User, Vulnerability } from '../types'
import { Badge, Card, SectionTitle } from '../components/Ui'

type Props = {
  users: User[]
  vulnerabilities: Vulnerability[]
}

function severityTone(severity: string): 'slate' | 'yellow' | 'green' | 'red' | 'blue' {
  if (severity === 'Crítica') return 'yellow'
  if (severity === 'Alta') return 'red'
  if (severity === 'Media') return 'blue'
  return 'slate'
}

export function TeamDetailPage({ users, vulnerabilities }: Props) {
  const params = useParams()
  const id = Number(params.id)
  const analyst = users.find((user) => user.id === id)
  const assigned = vulnerabilities.filter((item) => item.assigned_analyst_id === id)

  if (!analyst) {
    return (
      <div className="space-y-6">
        <SectionTitle title="Analista no encontrado" subtitle="El usuario solicitado no existe." />
        <Link to="/equipo" className="inline-flex rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
          Volver al equipo
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/equipo" className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
          ← Equipo
        </Link>
      </div>

      <Card className={analyst.active ? '' : 'bg-rose-50/70'}>
        <div className="flex items-start justify-between gap-3">
          <div>
            <h2 className="text-2xl font-semibold text-slate-900">{analyst.username}</h2>
            <p className="mt-1 text-sm text-slate-500">{analyst.email}</p>
          </div>
          <Badge tone={analyst.active ? 'green' : 'red'}>{analyst.active ? 'Activo' : 'Inactivo'}</Badge>
        </div>
        <div className="mt-4 grid gap-3 text-sm text-slate-600 md:grid-cols-3">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-400">Rol</p>
            <p className="mt-1 font-semibold text-slate-900 capitalize">{analyst.role}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-400">Última actividad</p>
            <p className="mt-1 font-semibold text-slate-900">{analyst.latest_activity}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-400">Vulnerabilidades</p>
            <p className="mt-1 font-semibold text-slate-900">{analyst.assigned_vulnerabilities ?? assigned.length}</p>
          </div>
        </div>
      </Card>

      <SectionTitle title="Vulnerabilidades asignadas" subtitle={`${assigned.length} vulnerabilidad(es) a cargo de ${analyst.username}.`} />

      <div className="grid gap-4 xl:grid-cols-2">
        {assigned.map((item) => (
          <Link key={item.id} to={`/vulnerabilidades/${item.id}`}>
            <Card className="h-full transition hover:-translate-y-0.5 hover:bg-slate-50">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-semibold text-slate-900">{item.cve}</h3>
                    {item.irc >= 8 ? <Badge tone="yellow">Crítica</Badge> : null}
                  </div>
                  <p className="mt-2 text-sm text-slate-600">{item.description}</p>
                </div>
                <Badge tone={severityTone(item.severity)}>{item.severity}</Badge>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-3 text-sm text-slate-600 md:grid-cols-4">
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-400">IRC</p>
                  <p className="mt-1 font-semibold text-slate-900">{item.irc.toFixed(1)}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-400">Estado</p>
                  <p className="mt-1 font-semibold text-slate-900">{item.status}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-400">Empresa</p>
                  <p className="mt-1 font-semibold text-slate-900">{item.company?.name || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-400">Tecnología</p>
                  <p className="mt-1 font-semibold text-slate-900">{item.affected_technology || '—'}</p>
                </div>
              </div>
            </Card>
          </Link>
        ))}
      </div>

      {assigned.length === 0 ? (
        <Card><p className="text-sm text-slate-500">Este analista no tiene vulnerabilidades asignadas.</p></Card>
      ) : null}
    </div>
  )
}
