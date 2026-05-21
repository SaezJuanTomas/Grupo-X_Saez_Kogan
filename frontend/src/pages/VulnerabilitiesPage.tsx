import { FormEvent, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import type { CompanySummary, Role, User, Vulnerability } from '../types'
import { Badge, Card, SectionTitle } from '../components/Ui'

type Props = {
  role: Role
  sessionUserId: number
  users: User[]
  companies: CompanySummary[]
  vulnerabilities: Vulnerability[]
  onCreateVulnerability: (payload: Omit<Vulnerability, 'id' | 'created_at' | 'updated_at' | 'company'>) => void
}

function severityTone(severity: string): 'slate' | 'yellow' | 'green' | 'red' | 'blue' {
  if (severity === 'Crítica') return 'yellow'
  if (severity === 'Alta') return 'red'
  if (severity === 'Media') return 'blue'
  return 'slate'
}

export function VulnerabilitiesPage({ role, sessionUserId, users, companies, vulnerabilities, onCreateVulnerability }: Props) {
  const visible = role === 'analyst' ? vulnerabilities.filter((item) => item.assigned_analyst_id === sessionUserId) : vulnerabilities
  const [cve, setCve] = useState('CVE-2025-005')
  const [description, setDescription] = useState('')
  const [irc, setIrc] = useState('7.5')
  const [severity, setSeverity] = useState('Alta')
  const [status, setStatus] = useState('Pendiente')
  const [companyId, setCompanyId] = useState(String(companies[0]?.id || vulnerabilities[0]?.company_id || 1))
  const [assignedAnalystId, setAssignedAnalystId] = useState(String(users.find((user) => user.role === 'analyst')?.id || ''))

  const companyOptions = useMemo(() => companies, [companies])

  function submit(event: FormEvent) {
    event.preventDefault()
    if (!description.trim()) return
    onCreateVulnerability({
      cve,
      description: description.trim(),
      irc: Number(irc),
      severity,
      status,
      company_id: Number(companyId),
      assigned_analyst_id: assignedAnalystId ? Number(assignedAnalystId) : null,
    })
    setDescription('')
  }

  return (
    <div className="space-y-6">
      <SectionTitle
        title="Vulnerabilidades"
        subtitle={role === 'admin' ? 'Vista completa con todos los casos del sistema.' : 'Solo casos asignados a tu usuario.'}
      />

      {role === 'admin' ? (
        <Card>
          <h3 className="text-lg font-semibold text-slate-900">Crear vulnerabilidad</h3>
          <form className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4" onSubmit={submit}>
            <input value={cve} onChange={(event) => setCve(event.target.value)} placeholder="CVE" className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none" />
            <input value={irc} onChange={(event) => setIrc(event.target.value)} type="number" step="0.1" min="0" max="10" placeholder="IRC" className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none" />
            <select value={severity} onChange={(event) => setSeverity(event.target.value)} className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none">
              <option>Crítica</option>
              <option>Alta</option>
              <option>Media</option>
              <option>Baja</option>
            </select>
            <select value={status} onChange={(event) => setStatus(event.target.value)} className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none">
              <option>Pendiente</option>
              <option>En progreso</option>
              <option>Resuelto</option>
            </select>
            <textarea value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Descripción" className="min-h-24 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none md:col-span-2 xl:col-span-2" />
            <select value={companyId} onChange={(event) => setCompanyId(event.target.value)} className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none">
              {companyOptions.map((company) => (
                <option key={company.id} value={company.id}>
                  {company.name}
                </option>
              ))}
            </select>
            <select value={assignedAnalystId} onChange={(event) => setAssignedAnalystId(event.target.value)} className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none">
              <option value="">Sin asignar</option>
              {users.filter((user) => user.role === 'analyst').map((user) => (
                <option key={user.id} value={user.id}>
                  {user.username}
                </option>
              ))}
            </select>
            <button type="submit" className="rounded-xl bg-slate-950 px-4 py-3 text-sm font-medium text-white hover:bg-slate-700 md:col-span-2 xl:col-span-4">
              Crear vulnerabilidad
            </button>
          </form>
        </Card>
      ) : null}

      <div className="grid gap-4 xl:grid-cols-2">
        {visible.map((item) => {
          const analyst = users.find((user) => user.id === item.assigned_analyst_id)
          const critical = item.irc >= 8

          return (
            <Link key={item.id} to={`/vulnerabilidades/${item.id}`}>
              <Card className={`h-full transition hover:-translate-y-0.5 hover:bg-slate-50 ${critical ? 'border-amber-200 bg-amber-50/70' : ''}`}>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-base font-semibold text-slate-900">{item.cve}</h3>
                      {critical ? <Badge tone="yellow">Alerta crítica</Badge> : null}
                    </div>
                    <p className="mt-2 text-sm text-slate-600">{item.description}</p>
                  </div>
                  <Badge tone={severityTone(item.severity) as 'slate'}>{item.severity}</Badge>
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
                    <p className="text-xs uppercase tracking-wide text-slate-400">Analista</p>
                    <p className="mt-1 font-semibold text-slate-900">{analyst?.username || 'Sin asignar'}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400">Empresa</p>
                    <p className="mt-1 font-semibold text-slate-900">{item.company?.name || 'N/A'}</p>
                  </div>
                </div>
              </Card>
            </Link>
          )
        })}
      </div>

      {visible.length === 0 ? <Card><p className="text-sm text-slate-500">No hay vulnerabilidades asignadas para mostrar.</p></Card> : null}
    </div>
  )
}
