import { Link } from 'react-router-dom'
import { FormEvent, useState } from 'react'
import type { CompanySummary, User } from '../types'
import { Card, SectionTitle } from '../components/Ui'
import { createCompany } from '../lib/api'

type Props = {
  companies: CompanySummary[]
  users: User[]
  onCreateCompany: (company: CompanySummary) => void
}

export function CompaniesPage({ companies, users, onCreateCompany }: Props) {
  const [name, setName] = useState('')
  const [sector, setSector] = useState('')
  const [contact, setContact] = useState('')
  const [technologiesInput, setTechnologiesInput] = useState('')

  function submit(event: FormEvent) {
    event.preventDefault()
    if (!name.trim() || !sector.trim() || !contact.trim()) return

    const technologies = technologiesInput
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)

    void createCompany({ name: name.trim(), sector: sector.trim(), contact: contact.trim(), technologies }).then((company) => {
      onCreateCompany(company)
      setName('')
      setSector('')
      setContact('')
      setTechnologiesInput('')
    })
  }

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

      <div className="grid gap-4 xl:grid-cols-2">
        {companies.map((company) => (
          <Card key={company.id}>
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-lg font-semibold text-slate-900">{company.name}</p>
                <p className="mt-1 text-sm text-slate-500">Sector: {company.sector}</p>
              </div>
              <div className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">ID {company.id}</div>
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
              <p>
                Analista responsable:{' '}
                {users.find((user) => user.id === company.assigned_analyst_id)?.username || 'Sin asignar'}
              </p>
            </div>

            <div className="mt-4">
              <Link to={`/empresas/${company.id}`} className="inline-flex rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
                Ver detalle
              </Link>
            </div>
          </Card>
        ))}
      </div>

      {companies.length === 0 ? (
        <Card>
          <p className="text-sm text-slate-500">No hay empresas cargadas.</p>
        </Card>
      ) : null}
    </div>
  )
}