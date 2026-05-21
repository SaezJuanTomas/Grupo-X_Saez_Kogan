export type Role = 'admin' | 'analyst'

export type User = {
  id: number
  username: string
  email: string
  role: Role
  active: boolean
  latest_activity: string
  assigned_vulnerabilities?: number
}

export type Company = {
  id: number
  name: string
  sector: string
  contact: string
  assigned_analyst_id?: number | null
}

export type Vulnerability = {
  id: number
  cve: string
  description: string
  irc: number
  severity: string
  status: string
  company_id: number
  assigned_analyst_id: number | null
  created_at: string
  updated_at: string
  company?: Company
}

export type CompanySummary = Company

export type Comment = {
  id: number
  vulnerability_id: number
  author_id: number
  text: string
  created_at: string
}

export type HistoryLog = {
  id: number
  vulnerability_id: number
  actor_id: number | null
  action: string
  detail: string
  created_at: string
}

export type DashboardStats = {
  critical: number
  pending: number
  resolved: number
  active_users: number
  severity_counts: Record<string, number>
  status_counts: Record<string, number>
  analyst_activity: Array<{ username: string; assigned: number; updated: number }>
  irc_distribution: Record<string, number>
}

export type SessionUser = {
  id: number
  username: string
  role: Role
}
