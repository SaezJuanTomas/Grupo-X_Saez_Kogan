import type { Comment, CompanySummary, DashboardStats, HistoryLog, SessionUser, User, Vulnerability } from '../types'

export const mockSessionUsers: Array<SessionUser & { password: string; email: string; active: boolean }> = [
  { id: 1, username: 'admin', password: '123', email: 'admin@grupox.local', role: 'admin', active: true },
  { id: 2, username: 'analyst', password: '123', email: 'analyst@grupox.local', role: 'analyst', active: true },
]

export const mockUsers: User[] = [
  { id: 1, username: 'admin', email: 'admin@grupox.local', role: 'admin', active: true, latest_activity: 'Revisó estadísticas', assigned_vulnerabilities: 0 },
  { id: 2, username: 'analyst', email: 'analyst@grupox.local', role: 'analyst', active: true, latest_activity: 'Actualizó estado de CVE-2025-001', assigned_vulnerabilities: 2 },
  { id: 3, username: 'juan', email: 'juan@grupox.local', role: 'analyst', active: true, latest_activity: 'Asignado a nueva vulnerabilidad', assigned_vulnerabilities: 1 },
  { id: 4, username: 'maria', email: 'maria@grupox.local', role: 'analyst', active: false, latest_activity: 'Cuenta inactiva temporalmente', assigned_vulnerabilities: 0 },
]

export const mockCompanies: CompanySummary[] = [
  { id: 1, name: 'Saez Logistics', sector: 'Logistica', contact: 'ciso@saezlogistics.local', assigned_analyst_id: 2 },
  { id: 2, name: 'Kogan Health', sector: 'Salud', contact: 'security@koganhealth.local', assigned_analyst_id: 3 },
  { id: 3, name: 'Grupo X Retail', sector: 'Comercio', contact: 'it@grupoxretail.local', assigned_analyst_id: 2 },
]

export const mockVulnerabilities: Vulnerability[] = [
  {
    id: 1,
    cve: 'CVE-2025-001',
    description: 'Exposición de panel interno por configuración débil de autenticación.',
    irc: 8.9,
    severity: 'Crítica',
    status: 'Pendiente',
    company_id: 1,
    assigned_analyst_id: 2,
    created_at: '2026-05-07T10:00:00Z',
    updated_at: '2026-05-10T10:00:00Z',
    company: { id: 1, name: 'Saez Logistics', sector: 'Logistica', contact: 'ciso@saezlogistics.local' },
  },
  {
    id: 2,
    cve: 'CVE-2025-002',
    description: 'Cabeceras de seguridad ausentes en una aplicación interna de reportes.',
    irc: 6.7,
    severity: 'Alta',
    status: 'En progreso',
    company_id: 2,
    assigned_analyst_id: 3,
    created_at: '2026-05-05T10:00:00Z',
    updated_at: '2026-05-10T22:00:00Z',
    company: { id: 2, name: 'Kogan Health', sector: 'Salud', contact: 'security@koganhealth.local' },
  },
  {
    id: 3,
    cve: 'CVE-2025-003',
    description: 'Dependencia desactualizada con riesgo de ejecución remota limitada.',
    irc: 5.2,
    severity: 'Media',
    status: 'Resuelto',
    company_id: 3,
    assigned_analyst_id: 2,
    created_at: '2026-05-02T10:00:00Z',
    updated_at: '2026-05-09T10:00:00Z',
    company: { id: 3, name: 'Grupo X Retail', sector: 'Comercio', contact: 'it@grupoxretail.local' },
  },
  {
    id: 4,
    cve: 'CVE-2025-004',
    description: 'Permisos excesivos en almacenamiento compartido.',
    irc: 4.1,
    severity: 'Baja',
    status: 'Pendiente',
    company_id: 1,
    assigned_analyst_id: 3,
    created_at: '2026-05-08T10:00:00Z',
    updated_at: '2026-05-10T14:00:00Z',
    company: { id: 1, name: 'Saez Logistics', sector: 'Logistica', contact: 'ciso@saezlogistics.local' },
  },
]

export const mockComments: Comment[] = [
  { id: 1, vulnerability_id: 1, author_id: 1, text: 'Prioridad alta. Validar mitigación esta semana.', created_at: '2026-05-09T10:00:00Z' },
  { id: 2, vulnerability_id: 1, author_id: 2, text: 'Estoy validando el acceso al panel y preparando evidencia.', created_at: '2026-05-09T13:00:00Z' },
  { id: 3, vulnerability_id: 2, author_id: 3, text: 'Identifiqué cabeceras faltantes. Propongo corregir con la próxima entrega.', created_at: '2026-05-10T12:00:00Z' },
  { id: 4, vulnerability_id: 3, author_id: 2, text: 'Cierre confirmado luego de aplicar actualización y pruebas.', created_at: '2026-05-08T12:00:00Z' },
]

export const mockHistory: HistoryLog[] = [
  { id: 1, vulnerability_id: 1, actor_id: 1, action: 'Asignado', detail: 'Asignado a analyst', created_at: '2026-05-07T12:00:00Z' },
  { id: 2, vulnerability_id: 1, actor_id: 2, action: 'Comentario agregado', detail: 'Se inició validación técnica', created_at: '2026-05-09T13:00:00Z' },
  { id: 3, vulnerability_id: 1, actor_id: 2, action: 'Estado cambiado', detail: 'Estado cambiado a Pendiente', created_at: '2026-05-10T10:00:00Z' },
  { id: 4, vulnerability_id: 2, actor_id: 3, action: 'Estado cambiado', detail: 'Estado cambiado a En progreso', created_at: '2026-05-10T12:00:00Z' },
  { id: 5, vulnerability_id: 3, actor_id: 2, action: 'Estado cambiado', detail: 'Estado cambiado a Resuelto', created_at: '2026-05-08T10:00:00Z' },
  { id: 6, vulnerability_id: 4, actor_id: 1, action: 'Asignado', detail: 'Asignado a juan', created_at: '2026-05-08T10:00:00Z' },
]

export const mockStats: DashboardStats = {
  critical: 1,
  pending: 2,
  resolved: 1,
  active_users: 3,
  severity_counts: { Crítica: 1, Alta: 1, Media: 1, Baja: 1 },
  status_counts: { Pendiente: 2, 'En progreso': 1, Resuelto: 1 },
  analyst_activity: [
    { username: 'analyst', assigned: 2, updated: 3 },
    { username: 'juan', assigned: 1, updated: 1 },
  ],
  irc_distribution: { '0-3': 0, '3-6': 2, '6-8': 1, '8-10': 1 },
}
