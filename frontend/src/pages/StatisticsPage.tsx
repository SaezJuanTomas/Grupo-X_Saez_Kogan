import type { DashboardStats } from '../types'
import { Card, MetricCard, SectionTitle } from '../components/Ui'

type Props = { stats: DashboardStats }

function Bar({ label, value, total }: { label: string; value: number; total: number }) {
  const width = total > 0 ? Math.max((value / total) * 100, value > 0 ? 12 : 0) : 0
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-sm text-slate-600">
        <span>{label}</span>
        <span>{value}</span>
      </div>
      <div className="h-2 rounded-full bg-slate-100">
        <div className="h-2 rounded-full bg-slate-900" style={{ width: `${width}%` }} />
      </div>
    </div>
  )
}

export function StatisticsPage({ stats }: Props) {
  const totalSeverity = Object.values(stats.severity_counts).reduce((sum, value) => sum + value, 0)
  const totalStatus = Object.values(stats.status_counts).reduce((sum, value) => sum + value, 0)

  return (
    <div className="space-y-6">
      <SectionTitle title="Estadísticas" subtitle="Resumen compacto basado en datos del backend o fallback local." />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Críticas" value={stats.critical} />
        <MetricCard label="Pendientes" value={stats.pending} />
        <MetricCard label="Resueltas" value={stats.resolved} />
        <MetricCard label="Usuarios activos" value={stats.active_users} />
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <Card>
          <SectionTitle title="Vulnerabilidades por severidad" />
          <div className="space-y-4">
            {Object.entries(stats.severity_counts).map(([label, value]) => (
              <Bar key={label} label={label} value={value} total={totalSeverity} />
            ))}
          </div>
        </Card>

        <Card>
          <SectionTitle title="Vulnerabilidades por estado" />
          <div className="space-y-4">
            {Object.entries(stats.status_counts).map(([label, value]) => (
              <Bar key={label} label={label} value={value} total={totalStatus} />
            ))}
          </div>
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

        <Card>
          <SectionTitle title="Distribución IRC" />
          <div className="space-y-4">
            {Object.entries(stats.irc_distribution).map(([label, value]) => (
              <Bar key={label} label={label} value={value} total={Object.values(stats.irc_distribution).reduce((sum, current) => sum + current, 0)} />
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
