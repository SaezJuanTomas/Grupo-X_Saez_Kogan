import type { User } from '../types'
import { Badge, Card, SectionTitle } from '../components/Ui'

type Props = { users: User[] }

export function TeamPage({ users }: Props) {
  const analysts = users.filter((user) => user.role === 'analyst')

  return (
    <div className="space-y-6">
      <SectionTitle title="Equipo" subtitle="Vista breve del equipo operativo." />

      <div className="grid gap-4 xl:grid-cols-2">
        {analysts.map((user) => (
          <Card key={user.id} className={`${user.active ? '' : 'bg-rose-50/70'}`}>
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-lg font-semibold text-slate-900">{user.username}</p>
                <p className="mt-1 text-sm text-slate-500">{user.email}</p>
              </div>
              <Badge tone={user.active ? 'green' : 'red'}>{user.active ? 'Activo' : 'Inactivo'}</Badge>
            </div>
            <p className="mt-4 text-sm text-slate-600">Última actividad: {user.latest_activity}</p>
            <p className="mt-2 text-sm text-slate-600">Vulnerabilidades asignadas: {user.assigned_vulnerabilities ?? 0}</p>
          </Card>
        ))}
      </div>
    </div>
  )
}
