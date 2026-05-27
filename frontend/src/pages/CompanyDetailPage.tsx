import { FormEvent, useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import type { CompanySummary, User, Vulnerability } from '../types'
import { Badge, Card, SectionTitle } from '../components/Ui'
import { updateCompany } from '../lib/api'

type Props = {
  companies: CompanySummary[]
  users: User[]
  vulnerabilities: Vulnerability[]
  onUpdateCompany: (id: number, company: CompanySummary) => void
}

export function CompanyDetailPage({ companies, users, vulnerabilities, onUpdateCompany }: Props) {
  const params = useParams()
  const id = Number(params.id)
  const company = companies.find((item) => item.id === id) || companies[0]
  const assignedVulnerabilities = useMemo(
    () => vulnerabilities.filter((item) => item.company_id === company?.id),
    [company?.id, vulnerabilities],
  )

  const [name, setName] = useState(company?.name || '')
  const [sector, setSector] = useState(company?.sector || '')
  const [contact, setContact] = useState(company?.contact || '')
  const [technologiesInput, setTechnologiesInput] = useState(company?.technologies?.join(', ') || '')
  const [assignedAnalystId, setAssignedAnalystId] = useState(String(company?.assigned_analyst_id || ''))

  useEffect(() => {
    setName(company?.name || '')
    setSector(company?.sector || '')
    setContact(company?.contact || '')
    setTechnologiesInput(company?.technologies?.join(', ') || '')
    setAssignedAnalystId(String(company?.assigned_analyst_id || ''))
  }, [company?.id, company?.name, company?.sector, company?.contact, company?.technologies, company?.assigned_analyst_id])

  if (!company) {
    return (
      <Card>
        <p className="text-sm text-slate-500">Empresa no encontrada.</p>
      </Card>
    )
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    if (!name.trim() || !sector.trim() || !contact.trim()) return

    const technologies = technologiesInput
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)

    void updateCompany(company.id, {
      name: name.trim(),
      sector: sector.trim(),
      contact: contact.trim(),
      technologies,
      assigned_analyst_id: assignedAnalystId ? Number(assignedAnalystId) : null,
    }).then((updatedCompany) => {
      onUpdateCompany(company.id, updatedCompany)
    })
  }

  const assignedAnalyst = users.find((user) => user.id === company.assigned_analyst_id)
  const analystOptions = users.filter((user) => user.role === 'analyst')

  return (
    <div className="space-y-6">
      <SectionTitle title="Detalle de empresa" subtitle="Información básica y vulnerabilidades asociadas." />

      <div className="grid gap-6 xl:grid-cols-[1fr_1.1fr]">
        <Card>
          <div className="flex items-start justify-between gap-3">
            <div>
              <h2 className="text-2xl font-semibold text-slate-900">{company.name}</h2>
              <p className="mt-1 text-sm text-slate-500">Sector: {company.sector}</p>
            </div>
            <Badge tone="blue">ID {company.id}</Badge>
          </div>

          <form className="mt-5 grid gap-3" onSubmit={submit}>
            <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Nombre" className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none" />
            <input value={sector} onChange={(event) => setSector(event.target.value)} placeholder="Sector" className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none" />
            <input value={contact} onChange={(event) => setContact(event.target.value)} placeholder="Contacto" className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none" />
            <input value={technologiesInput} onChange={(event) => setTechnologiesInput(event.target.value)} placeholder="Tecnologías (separadas por coma)" className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none" />
            <select value={assignedAnalystId} onChange={(event) => setAssignedAnalystId(event.target.value)} className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none">
              <option value="">Sin asignar</option>
              {analystOptions.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.username}
                </option>
              ))}
            </select>
            <button type="submit" className="rounded-xl bg-slate-950 px-4 py-3 text-sm font-medium text-white hover:bg-slate-700">
              Guardar cambios
            </button>
          </form>

          <div className="mt-5 text-sm text-slate-600">
            <p>Contacto actual: {company.contact}</p>
            {company.technologies?.length ? (
              <div className="mt-3">
                <p className="mb-1.5 font-medium text-slate-700">Tecnologías</p>
                <div className="flex flex-wrap gap-1.5">
                  {company.technologies.map((tech) => (
                    <span key={tech} className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">{tech}</span>
                  ))}
                </div>
              </div>
            ) : null}
            <p className="mt-3">Analista responsable: {assignedAnalyst?.username || 'Sin asignar'}</p>
          </div>

          <div className="mt-5">
            <Link to="/empresas" className="inline-flex rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
              Volver
            </Link>
          </div>
        </Card>

        <Card>
          <SectionTitle title="Vulnerabilidades asignadas" subtitle="Casos vinculados a esta empresa." />
          <div className="space-y-3">
            {assignedVulnerabilities.map((item) => (
              <Link key={item.id} to={`/vulnerabilidades/${item.id}`} className={`block rounded-xl border p-4 transition hover:bg-slate-50 ${item.irc >= 8 ? 'border-amber-200 bg-amber-50' : 'border-slate-200 bg-white'}`}>
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-slate-900">{item.cve}</p>
                  <Badge tone={item.irc >= 8 ? 'yellow' : 'slate'}>{item.status}</Badge>
                </div>
                <p className="mt-2 text-sm text-slate-600">{item.description}</p>
              </Link>
            ))}
            {assignedVulnerabilities.length === 0 ? <p className="text-sm text-slate-500">No hay vulnerabilidades asociadas.</p> : null}
          </div>
        </Card>
      </div>
    </div>
  )
}