import axios from 'axios'
import type { Comment, CompanySummary, DashboardStats, HistoryLog, User, Vulnerability } from '../types'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

let isRefreshing = false
let pendingRequests: Array<(token: string) => void> = []

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('grupo-x-token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem('grupo-x-refresh-token')
      if (!refreshToken) {
        localStorage.removeItem('grupo-x-token')
        localStorage.removeItem('grupo-x-refresh-token')
        localStorage.removeItem('grupo-x-session')
        window.location.href = '/login'
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve) => {
          pendingRequests.push((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(http(originalRequest))
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const { data } = await axios.post(`${http.defaults.baseURL}/auth/refresh`, {
          refresh_token: refreshToken,
        })
        localStorage.setItem('grupo-x-token', data.access_token)
        localStorage.setItem('grupo-x-refresh-token', data.refresh_token)
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`
        pendingRequests.forEach((cb) => cb(data.access_token))
        pendingRequests = []
        return http(originalRequest)
      } catch {
        localStorage.removeItem('grupo-x-token')
        localStorage.removeItem('grupo-x-refresh-token')
        localStorage.removeItem('grupo-x-session')
        window.location.href = '/login'
        return Promise.reject(error)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  },
)

export function setToken(token: string | null) {
  if (token) {
    localStorage.setItem('grupo-x-token', token)
  } else {
    localStorage.removeItem('grupo-x-token')
  }
}

export type LoginPayload = { username: string; password: string }
export type LoginResult = { access_token: string; refresh_token: string; token_type: string; user_id: number; username: string; role: string }

export async function login(payload: LoginPayload): Promise<LoginResult> {
  const { data } = await http.post<LoginResult>('/auth/login', payload)
  return data
}

export async function logout(): Promise<void> {
  try {
    await http.post('/auth/logout')
  } catch {
    // Ignore logout errors
  }
}

export async function getUsers(): Promise<User[]> {
  const { data } = await http.get<User[]>('/usuarios')
  return data
}

export async function getCompanies(): Promise<CompanySummary[]> {
  const { data } = await http.get<CompanySummary[]>('/empresas')
  return data
}

export async function getCompany(id: number): Promise<CompanySummary> {
  const { data } = await http.get<CompanySummary>(`/empresas/${id}`)
  return data
}

export async function createCompany(payload: { name: string; sector: string; contact: string; technologies?: string[]; assigned_analyst_id?: number | null }): Promise<CompanySummary> {
  const { data } = await http.post<CompanySummary>('/empresas', payload)
  return data
}

export async function updateCompany(id: number, payload: Partial<Omit<CompanySummary, 'id'>>): Promise<CompanySummary> {
  const { data } = await http.patch<CompanySummary>(`/empresas/${id}`, payload)
  return data
}

export async function getVulnerabilities(role?: string, userId?: number): Promise<Vulnerability[]> {
  const params: Record<string, string> = { page: '1', page_size: '200' }
  if (role) params.role = role
  if (userId) params.user_id = String(userId)
  const { data } = await http.get<Vulnerability[]>('/vulnerabilidades', { params })
  return data
}

export async function getVulnerability(id: number): Promise<Vulnerability> {
  const { data } = await http.get<Vulnerability>(`/vulnerabilidades/${id}`)
  return data
}

export async function createVulnerability(payload: Omit<Vulnerability, 'id' | 'created_at' | 'updated_at' | 'company'>): Promise<Vulnerability> {
  const { data } = await http.post<Vulnerability>('/vulnerabilidades', payload)
  return data
}

export async function updateVulnerability(id: number, payload: Partial<Vulnerability>): Promise<Vulnerability> {
  const { data } = await http.patch<Vulnerability>(`/vulnerabilidades/${id}`, payload)
  return data
}

export async function deleteVulnerability(id: number): Promise<void> {
  await http.delete(`/vulnerabilidades/${id}`)
}

export async function getComments(vulnerabilityId: number): Promise<Comment[]> {
  const { data } = await http.get<Comment[]>('/comentarios', { params: { vulnerability_id: vulnerabilityId } })
  return data
}

export async function createComment(vulnerabilityId: number, authorId: number, text: string): Promise<Comment> {
  const { data } = await http.post<Comment>(`/vulnerabilidades/${vulnerabilityId}/comentarios`, {
    vulnerability_id: vulnerabilityId,
    author_id: authorId,
    text,
  })
  return data
}

export async function getHistory(vulnerabilityId: number): Promise<HistoryLog[]> {
  const { data } = await http.get<HistoryLog[]>('/historial', { params: { vulnerability_id: vulnerabilityId } })
  return data
}

export async function getStats(): Promise<DashboardStats> {
  const { data } = await http.get<DashboardStats>('/estadisticas')
  return data
}

export type TrendPoint = { date: string; count: number }
export type TrendsData = { created: TrendPoint[]; resolved: TrendPoint[] }

export async function getTrends(days = 7): Promise<TrendsData> {
  const { data } = await http.get<TrendsData>('/estadisticas/tendencias', { params: { days } })
  return data
}

export async function createUser(payload: { username: string; email: string; role: 'admin' | 'analyst'; password: string }): Promise<User> {
  const { data } = await http.post<User>('/usuarios', payload)
  return data
}

export async function updateUser(id: number, payload: Partial<User>): Promise<User> {
  const { data } = await http.patch<User>(`/usuarios/${id}`, payload)
  return data
}
