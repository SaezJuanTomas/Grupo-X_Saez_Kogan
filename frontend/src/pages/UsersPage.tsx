import { FormEvent, useState } from 'react'
import type { User } from '../types'
import { Badge, Card, SectionTitle } from '../components/Ui'

type Props = {
  users: User[]
  onToggleActive: (userId: number) => void
  onCreateUser: (payload: { username: string; email: string; role: 'admin' | 'analyst'; password: string }) => void
}

export function UsersPage({ users, onToggleActive, onCreateUser }: Props) {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [role, setRole] = useState<'admin' | 'analyst'>('analyst')

  function submit(event: FormEvent) {
    event.preventDefault()
    if (!username.trim() || !email.trim()) return
    onCreateUser({ username: username.trim(), email: email.trim(), role, password: '123' })
    setUsername('')
    setEmail('')
    setRole('analyst')
  }

  return (
    <div className="space-y-6">
      <SectionTitle title="Gestión de usuarios" subtitle="Alta, activación y desactivación de cuentas mock." />

      <Card>
        <h3 className="text-lg font-semibold text-slate-900">Crear usuario</h3>
        <form className="mt-4 grid gap-3 md:grid-cols-4" onSubmit={submit}>
          <input value={username} onChange={(event) => setUsername(event.target.value)} placeholder="Usuario" className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none" />
          <input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Email" className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none" />
          <select value={role} onChange={(event) => setRole(event.target.value as 'admin' | 'analyst')} className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none">
            <option value="analyst">Analyst</option>
            <option value="admin">Admin</option>
          </select>
          <button type="submit" className="rounded-xl bg-slate-950 px-4 py-3 text-sm font-medium text-white hover:bg-slate-700">Crear</button>
        </form>
      </Card>

      <div className="grid gap-4 xl:grid-cols-2">
        {users.map((user) => (
          <Card key={user.id} className={!user.active ? 'bg-rose-50/70' : ''}>
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-lg font-semibold text-slate-900">{user.username}</p>
                <p className="mt-1 text-sm text-slate-500">{user.email}</p>
              </div>
              <Badge tone={user.active ? 'green' : 'red'}>{user.active ? 'Activo' : 'Inactivo'}</Badge>
            </div>
            <div className="mt-4 grid gap-2 text-sm text-slate-600">
              <p>Rol: {user.role}</p>
              <p>Asignadas: {user.assigned_vulnerabilities ?? 0}</p>
              <p>Actividad: {user.latest_activity}</p>
            </div>
            <div className="mt-4 flex gap-2">
              <button type="button" onClick={() => onToggleActive(user.id)} className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
                {user.active ? 'Desactivar' : 'Reactivar'}
              </button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
