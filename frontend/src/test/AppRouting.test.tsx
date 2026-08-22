import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import { App } from '../App'

vi.mock('../lib/api', () => ({
  setToken: vi.fn(),
  login: vi.fn(),
  logout: vi.fn(),
  getUsers: vi.fn(async () => []),
  getCompanies: vi.fn(async () => []),
  getVulnerabilities: vi.fn(async () => []),
  getStats: vi.fn(async () => ({ critical: 0, pending: 0, resolved: 0, active_users: 0, severity_counts: {}, status_counts: {}, analyst_activity: [], irc_distribution: {} })),
  getComments: vi.fn(async () => []),
  getHistory: vi.fn(async () => []),
  createCompany: vi.fn(),
  createUser: vi.fn(),
  createVulnerability: vi.fn(),
  deleteVulnerability: vi.fn(),
  reactivateCompany: vi.fn(),
  softDeleteCompany: vi.fn(),
  updateUser: vi.fn(),
  updateVulnerability: vi.fn(),
}))

function renderApp(initialRoute: string) {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </MemoryRouter>,
  )
}

describe('App routing', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('renders the public landing at / when unauthenticated', () => {
    renderApp('/')
    expect(screen.getByText(/Detectá, priorizá y gestioná vulnerabilidades/)).toBeInTheDocument()
    expect(screen.queryByText('Iniciar sesión', { selector: 'form button' })).toBeNull()
  })

  it('redirects unknown routes to / when unauthenticated', () => {
    renderApp('/vulnerabilidades')
    expect(screen.getByText(/Detectá, priorizá y gestioná vulnerabilidades/)).toBeInTheDocument()
  })

  it('shows the login page at /login when unauthenticated', () => {
    renderApp('/login')
    expect(screen.getByText('Iniciar sesión')).toBeInTheDocument()
    expect(screen.getByText('Entrar')).toBeInTheDocument()
  })

  it('keeps the dashboard at /inicio when authenticated', async () => {
    localStorage.setItem('grupo-x-session', JSON.stringify({ id: 1, username: 'admin', role: 'admin' }))
    renderApp('/inicio')
    const heading = await screen.findByText('Bienvenido, admin')
    expect(heading).toBeInTheDocument()
  })

  it('sends authenticated users from /login to their dashboard', async () => {
    localStorage.setItem('grupo-x-session', JSON.stringify({ id: 1, username: 'admin', role: 'admin' }))
    renderApp('/login')
    const heading = await screen.findByText('Bienvenido, admin')
    expect(heading).toBeInTheDocument()
  })

  it('allows an authenticated user to view the landing at / with their session in the header', () => {
    localStorage.setItem('grupo-x-session', JSON.stringify({ id: 2, username: 'juan', role: 'analyst' }))
    renderApp('/')
    expect(screen.getByText(/Detectá, priorizá y gestioná vulnerabilidades/)).toBeInTheDocument()
    expect(screen.getByText(/juan · Analista/)).toBeInTheDocument()
  })
})
