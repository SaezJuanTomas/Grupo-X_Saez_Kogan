import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import type { DashboardStats } from '../types'
import { Card, MetricCard, SectionTitle } from '../components/Ui'

type Props = { stats: DashboardStats }

const COLORS = ['#0f172a', '#e11d48', '#f59e0b', '#3b82f6', '#10b981']

export function StatisticsPage({ stats }: Props) {
  const severityData = Object.entries(stats.severity_counts).map(([name, value]) => ({ name, value }))
  const statusData = Object.entries(stats.status_counts).map(([name, value]) => ({ name, value }))
  const ircData = Object.entries(stats.irc_distribution).map(([name, value]) => ({ name, value }))

  return (
    <div className="space-y-6">
      <SectionTitle title="Estadísticas" subtitle="Resumen basado en datos del backend." />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Críticas" value={stats.critical} />
        <MetricCard label="Pendientes" value={stats.pending} />
        <MetricCard label="Resueltas" value={stats.resolved} />
        <MetricCard label="Usuarios activos" value={stats.active_users} />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <SectionTitle title="Vulnerabilidades por severidad" />
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={severityData}>
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#0f172a" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <SectionTitle title="Vulnerabilidades por estado" />
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={statusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                {statusData.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <SectionTitle title="Distribución IRC" />
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={ircData}>
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#e11d48" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <SectionTitle title="Actividad de analistas" />
          <div className="space-y-3">
            {stats.analyst_activity.map((item) => (
              <div key={item.username} className="rounded-2xl bg-slate-50 p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium text-slate-900">{item.username}</p>
                  <p className="text-sm text-slate-500">Actualizaciones: {item.updated}</p>
                </div>
                <p className="mt-2 text-sm text-slate-600">Asignadas: {item.assigned}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
