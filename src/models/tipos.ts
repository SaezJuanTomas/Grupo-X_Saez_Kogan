// ===== AUTENTICACIÓN =====
export type UserRole = 'admin' | 'analyst'

export interface Usuario {
  id: number
  username: string
  role: UserRole
  company_id: number
  active: boolean
}

export interface LoginCredentials {
  username: string
  password: string
}

// ===== ORGANIZACIONAL =====
export interface Empresa {
  id: number
  name: string
}

export interface Proyecto {
  id: number
  titulo: string
  descripcion: string
  estado: 'activo' | 'completado' | 'pausado'
}

// ===== VULNERABILIDADES =====
export type VulnerabilidadStatus = 'Pendiente' | 'En revisión' | 'Resuelto' | 'Archivado'
export type VulnerabilidadSeverity = 'Alta' | 'Media' | 'Baja'

export interface Vulnerabilidad {
  id: number
  cve: string
  description: string
  irc: number
  severity: VulnerabilidadSeverity
  status: VulnerabilidadStatus
  assigned_to: number | null
  company_id: number
  updated_at: string
  created_at?: string
}

// Legacy compatibility
export interface VulnerabilidadLegacy {
  id: number
  cve: string
  irc: string
  ircScore: number
  activoAfectado: string
  asignadoA: string
  descripcion?: string
  estado?: 'activo' | 'resuelto' | 'pendiente'
}

// ===== COMENTARIOS E HISTORIA =====
export interface Comentario {
  id: number
  vulnerability_id: number
  author: string
  author_id: number
  content: string
  created_at: string
}

export interface HistorialLog {
  id: number
  vulnerability_id: number
  action: string
  created_at: string
  changed_by?: string
}
