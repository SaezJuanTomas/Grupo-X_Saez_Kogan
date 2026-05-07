// API Service - Backend integration
// Simple fetch wrapper para comunicación con FastAPI backend

const API_BASE_URL = 'http://localhost:8000/api'

// ===== HELPER =====
async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers
    },
    ...options
  })

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`)
  }

  return response.json() as Promise<T>
}

// ===== VULNERABILIDADES =====
export async function getVulnerabilities() {
  return apiFetch('/vulnerabilities')
}

export async function getVulnerabilityById(id: number) {
  return apiFetch(`/vulnerabilities/${id}`)
}

export async function createVulnerability(data: any) {
  return apiFetch('/vulnerabilities', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

export async function updateVulnerability(id: number, data: any) {
  return apiFetch(`/vulnerabilities/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  })
}

export async function deleteVulnerability(id: number) {
  return apiFetch(`/vulnerabilities/${id}`, {
    method: 'DELETE'
  })
}

// ===== COMENTARIOS =====
export async function getComments(vulnerabilityId: number) {
  return apiFetch(`/vulnerabilities/${vulnerabilityId}/comments`)
}

export async function createComment(vulnerabilityId: number, data: { author_id: number; content: string }) {
  return apiFetch(`/vulnerabilities/${vulnerabilityId}/comments`, {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

export async function deleteComment(vulnerabilityId: number, commentId: number) {
  return apiFetch(`/vulnerabilities/${vulnerabilityId}/comments/${commentId}`, {
    method: 'DELETE'
  })
}

// ===== HISTORIAL =====
export async function getHistory(vulnerabilityId: number) {
  return apiFetch(`/vulnerabilities/${vulnerabilityId}/history`)
}

// ===== USUARIOS =====
export async function getUsers() {
  return apiFetch('/users')
}

export async function getUserById(id: number) {
  return apiFetch(`/users/${id}`)
}

export async function createUser(data: any) {
  return apiFetch('/users', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

export async function updateUser(id: number, data: any) {
  return apiFetch(`/users/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  })
}

export async function deactivateUser(id: number) {
  return apiFetch(`/users/${id}/deactivate`, {
    method: 'POST'
  })
}

export async function activateUser(id: number) {
  return apiFetch(`/users/${id}/activate`, {
    method: 'POST'
  })
}

// ===== EMPRESAS =====
export async function getCompanies() {
  return apiFetch('/companies')
}

export async function getCompanyById(id: number) {
  return apiFetch(`/companies/${id}`)
}

export async function createCompany(data: any) {
  return apiFetch('/companies', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

// ===== ESTADÍSTICAS =====
export async function getDashboardStats() {
  return apiFetch('/stats/dashboard')
}

export async function getVulnerabilityStats() {
  return apiFetch('/stats/vulnerabilities')
}
