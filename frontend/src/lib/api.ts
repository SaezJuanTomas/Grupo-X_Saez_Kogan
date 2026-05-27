import type { Comment, CompanySummary, DashboardStats, HistoryLog, User, Vulnerability } from '../types'
import { mockComments, mockCompanies, mockHistory, mockStats, mockUsers, mockVulnerabilities } from '../data/mockData'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_URL}${path}`)
    if (!response.ok) throw new Error('Request failed')
    return (await response.json()) as T
  } catch {
    return fallback
  }
}

export async function getUsers(): Promise<User[]> {
  return request('/usuarios', mockUsers)
}

export async function getCompanies(): Promise<CompanySummary[]> {
  return request('/empresas', mockCompanies)
}

export async function getCompany(id: number): Promise<CompanySummary | undefined> {
  const fallback = mockCompanies.find((item) => item.id === id) || mockCompanies[0]
  return request(`/empresas/${id}`, fallback)
}

export async function createCompany(payload: Omit<CompanySummary, 'id'>): Promise<CompanySummary> {
  try {
    const response = await fetch(`${API_URL}/empresas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!response.ok) throw new Error('Request failed')
    return (await response.json()) as CompanySummary
  } catch {
    return {
      id: Date.now(),
      name: payload.name,
      sector: payload.sector,
      contact: payload.contact,
      technologies: payload.technologies ?? [],
    }
  }
}

export async function updateCompany(id: number, payload: Partial<Omit<CompanySummary, 'id'>>): Promise<CompanySummary> {
  try {
    const response = await fetch(`${API_URL}/empresas/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!response.ok) throw new Error('Request failed')
    return (await response.json()) as CompanySummary
  } catch {
    const fallback = mockCompanies.find((item) => item.id === id) as CompanySummary
    return { ...fallback, ...payload, id }
  }
}

export async function getVulnerabilities(role?: string, userId?: number): Promise<Vulnerability[]> {
  const params = new URLSearchParams()
  if (role) params.set('role', role)
  if (userId) params.set('user_id', String(userId))
  const suffix = params.toString() ? `?${params.toString()}` : ''
  return request(`/vulnerabilidades${suffix}`, mockVulnerabilities)
}

export async function getVulnerability(id: number): Promise<Vulnerability | undefined> {
  const fallback = mockVulnerabilities.find((item) => item.id === id) || mockVulnerabilities[0]
  return request(`/vulnerabilidades/${id}`, fallback)
}

export async function getComments(vulnerabilityId: number): Promise<Comment[]> {
  const fallback = mockComments.filter((comment) => comment.vulnerability_id === vulnerabilityId)
  return request(`/comentarios?vulnerability_id=${vulnerabilityId}`, fallback)
}

export async function getHistory(vulnerabilityId: number): Promise<HistoryLog[]> {
  const fallback = mockHistory.filter((item) => item.vulnerability_id === vulnerabilityId)
  return request(`/historial?vulnerability_id=${vulnerabilityId}`, fallback)
}

export async function getStats(): Promise<DashboardStats> {
  return request('/estadisticas', mockStats)
}

export async function createComment(vulnerabilityId: number, authorId: number, text: string): Promise<Comment> {
  try {
    const response = await fetch(`${API_URL}/vulnerabilidades/${vulnerabilityId}/comentarios`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vulnerability_id: vulnerabilityId, author_id: authorId, text }),
    })
    if (!response.ok) throw new Error('Request failed')
    return (await response.json()) as Comment
  } catch {
    return {
      id: Date.now(),
      vulnerability_id: vulnerabilityId,
      author_id: authorId,
      text,
      created_at: new Date().toISOString(),
    }
  }
}

export async function createVulnerability(payload: Omit<Vulnerability, 'id' | 'created_at' | 'updated_at' | 'company'>): Promise<Vulnerability> {
  try {
    const response = await fetch(`${API_URL}/vulnerabilidades`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!response.ok) throw new Error('Request failed')
    return (await response.json()) as Vulnerability
  } catch {
    return {
      id: Date.now(),
      ...payload,
      affected_technology: payload.affected_technology ?? null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
  }
}

export async function updateVulnerability(id: number, payload: Partial<Vulnerability>): Promise<Vulnerability> {
  try {
    const response = await fetch(`${API_URL}/vulnerabilidades/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!response.ok) throw new Error('Request failed')
    return (await response.json()) as Vulnerability
  } catch {
    return {
      ...(mockVulnerabilities.find((item) => item.id === id) as Vulnerability),
      ...payload,
      id,
      created_at: mockVulnerabilities.find((item) => item.id === id)?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
  }
}

export async function updateUser(id: number, payload: Partial<User>): Promise<User> {
  try {
    const response = await fetch(`${API_URL}/usuarios/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!response.ok) throw new Error('Request failed')
    return (await response.json()) as User
  } catch {
    const fallback = mockUsers.find((item) => item.id === id) as User
    return { ...fallback, ...payload, id }
  }
}

export async function createUser(payload: { username: string; email: string; role: 'admin' | 'analyst'; password: string }): Promise<User> {
  try {
    const response = await fetch(`${API_URL}/usuarios`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!response.ok) throw new Error('Request failed')
    return (await response.json()) as User
  } catch {
    return {
      id: Date.now(),
      username: payload.username,
      email: payload.email,
      role: payload.role,
      active: true,
      latest_activity: 'Usuario creado manualmente',
      assigned_vulnerabilities: 0,
    }
  }
}
