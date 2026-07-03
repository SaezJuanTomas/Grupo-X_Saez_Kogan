import { Link } from 'react-router-dom'
import { FormEvent, useMemo, useState } from 'react'
import type { CompanySummary, User, Vulnerability } from '../types'
import { Card, SectionTitle } from '../components/Ui'

type Props = {
  companies: CompanySummary[]
  users: User[]
  vulnerabilities: Vulnerability[]
  onCreateCompany: (payload: { name: string; sector: string; contact: string; technologies?: string[] }) => void
  onSoftDeleteCompany: (id: number) => void
  onReactivateCompany: (id: number) => void
}

export function CompaniesPage({ companies, users, vulnerabilities, onCreateCompany, onSoftDeleteCompany, onReactivateCompany }: Props) {
  const [showInactive, setShowInactive] = useState(false)
  const [name, setName] = useState('')
  const [sector, setSector] = useState('')
  const [contact, setContact] = useState('')
  const [technologiesInput, setTechnologiesInput] = useState('')

  const filteredCompanies = useMemo(() => {
    if (showInactive) return companies
    return companies.filter((c) => c.is_active !== false)
  }, [companies, showInactive])

  const companyVulnCounts = useMemo(() => {
    const counts: Record<number, number> = {}
    for (const v of vulnerabilities) {
      counts[v.company_id] = (counts[v.company_id] || 0) + 1
    }
    return counts
  }, [vulnerabilities])

  function submit(event: FormEvent) {
    event.preventDefault()
    if (!name.trim() || !sector.trim() || !contact.trim()) return

    const technologies = technologiesInput
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)

    onCreateCompany({ name: name.trim(), sector: sector.trim(), contact: contact.trim(), technologies })
    setName('')
    setSector('')
    setContact('')
    setTechnologiesInput('')
  }

  const activeCount = companies.filter((c) => c.is_active !== false).length
  const inactiveCount = companies.length - activeCount

  return (
    <div className="space-y-6">
      <SectionTitle title="Empresas" subtitle="Organizaciones registradas y asociadas a las vulnerabilidades." />

      <Card>
        <h3 className="text-lg font-semibold text-slate-900">Crear empresa</h3>
        <form className="mt-4 grid gap-3 md:grid-cols-3" onSubmit={submit}>
          <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Nombre" className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none" />
          <input value={sector} onChange={(event) => setSector(event.target.value)} placeholder="Sector" className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none" />
          <input value={contact} onChange={(event) => setContact(event.target.value)} placeholder="Contacto" className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none" />
          <input value={technologiesInput} onChange={(event) => setTechnologiesInput(event.target.value)} placeholder="Tecnologías (separadas por coma)" className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none md:col-span-3" />
          <button type="submit" className="rounded-xl bg-slate-950 px-4 py-3 text-sm font-medium text-white hover:bg-slate-700 md:col-span-3">
            Crear empresa
          </button>
        </form>
      </Card>

      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-slate-500">
          {showInactive ? `Mostrando todas (${activeCount} activas, ${inactiveCount} inactivas)` : `Mostrando activas (${activeCount})`}
        </p>
        <button
          type="button"
          onClick={() => setShowInactive(!showInactive)}
          className={`rounded-xl border px-4 py-2 text-sm font-medium transition ${showInactive ? 'border-slate-950 bg-slate-950 text-white' : 'border-slate-200 text-slate-700 hover:bg-slate-50'}`}
        >
          {showInactive ? 'Solo activas' : 'Mostrar todas'}
        </button>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        {filteredCompanies.map((company) => {
          const isInactive = company.is_active === false
          const vulnCount = companyVulnCounts[company.id] || 0
          const analyst = users.find((user) => user.id === company.assigned_analyst_id)

          return (
            <Card key={company.id} className={isInactive ? 'border-slate-200 bg-slate-50 opacity-70' : ''}>
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="text-lg font-semibold text-slate-900">{company.name}</p>
                    {isInactive ? <span className="rounded-full bg-rose-100 px-2.5 py-0.5 text-xs font-medium text-rose-700">Inactiva</span> : null}
                  </div>
                  <p className="mt-1 text-sm text-slate-500">Sector: {company.sector}</p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">{vulnCount} vuln.</span>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">ID {company.id}</span>
                </div>
              </div>

              <div className="mt-4 grid gap-2 text-sm text-slate-600">
                <p>Contacto: {company.contact}</p>
                {company.technologies?.length ? (
                  <div className="flex flex-wrap gap-1.5">
                    {company.technologies.map((tech) => (
                      <span key={tech} className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">{tech}</span>
                    ))}
                  </div>
                ) : null}
                <p>Analista: {analyst?.username || 'Sin asignar'}</p>
              </div>

              <div className="mt-4 flex flex-wrap items-center gap-2">
                <Link to={`/empresas/${company.id}`} className="inline-flex rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
                  Ver detalle
                </Link>

                {isInactive ? (
                  <button
                    type="button"
                    onClick={() => onReactivateCompany(company.id)}
                    className="inline-flex rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-100"
                  >
                    Reactivar
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={() => { if (confirm(`¿Desactivar ${company.name}?`)) onSoftDeleteCompany(company.id) }}
                    className="inline-flex rounded-xl border border-rose-200 px-4 py-2 text-sm font-medium text-rose-600 hover:bg-rose-50"
                  >
                    Desactivar
                  </button>
                )}

                {vulnCount === 0 && !isInactive ? (
                  <span className="inline-flex rounded-xl bg-amber-50 px-4 py-2 text-sm font-medium text-amber-700">
                    Sin vulnerabilidades (se buscarán automáticamente)
                  </span>
                ) : null}
              </div>
            </Card>
          )
        })}
      </div>

      {filteredCompanies.length === 0 ? (
        <Card>
          <p className="text-sm text-slate-500">
            {showInactive ? 'No hay empresas cargadas.' : 'No hay empresas activas.'}
          </p>
        </Card>
      ) : null}
    </div>
  )
}