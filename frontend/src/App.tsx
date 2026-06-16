import { useEffect, useState } from 'react'
import { Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Layout } from './components/Layout'
import { LoginPage } from './pages/LoginPage'
import { DashboardPage } from './pages/DashboardPage'
import { StatisticsPage } from './pages/StatisticsPage'
import { TeamPage } from './pages/TeamPage'
import { TeamDetailPage } from './pages/TeamDetailPage'
import { UsersPage } from './pages/UsersPage'
import { CompaniesPage } from './pages/CompaniesPage'
import { CompanyDetailPage } from './pages/CompanyDetailPage'
import { VulnerabilitiesPage } from './pages/VulnerabilitiesPage'
import { VulnerabilityDetailPage } from './pages/VulnerabilityDetailPage'
import { createCompany as createCompanyRequest, createUser as createUserRequest, createVulnerability as createVulnerabilityRequest, deleteVulnerability as deleteVulnerabilityRequest, getComments, getCompanies, getHistory, getStats, getUsers, getVulnerabilities, updateUser as updateUserRequest, updateVulnerability as updateVulnerabilityRequest } from './lib/api'
import type { Comment, CompanySummary, DashboardStats, HistoryLog, User, Vulnerability } from './types'

type Store = {
  users: User[]
  companies: CompanySummary[]
  vulnerabilities: Vulnerability[]
  comments: Comment[]
  history: HistoryLog[]
  stats: DashboardStats | null
}

const defaultStore: Store = {
  users: [],
  companies: [],
  vulnerabilities: [],
  comments: [],
  history: [],
  stats: null,
}

export function App() {
  const { user: sessionUser, login, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [error, setError] = useState<string | null>(null)
  const [store, setStore] = useState<Store>(defaultStore)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!sessionUser) return
    const currentUser = sessionUser
    let mounted = true

    async function fetchData() {
      setLoading(true)
      try {
        const [users, companies, vulnerabilities, stats] = await Promise.all([
          currentUser.role === 'admin' ? getUsers() : Promise.resolve([] as User[]),
          getCompanies(),
          getVulnerabilities(currentUser.role, currentUser.role === 'analyst' ? currentUser.id : undefined),
          getStats(),
        ])

        let comments: Comment[] = []
        let history: HistoryLog[] = []
        if (vulnerabilities[0]) {
          comments = await getComments(vulnerabilities[0].id)
          history = await getHistory(vulnerabilities[0].id)
        }

        if (mounted) {
          setStore({ users, companies, vulnerabilities, comments, history, stats })
        }
      } catch {
        if (mounted) {
          setError('Error al cargar datos')
        }
      } finally {
        if (mounted) setLoading(false)
      }
    }

    fetchData()

    return () => { mounted = false }
  }, [sessionUser, location.pathname])

  async function handleLogin(username: string, password: string) {
    await login(username, password)
    navigate('/')
  }

  async function handleLogout() {
    await logout()
    setStore(defaultStore)
    setError(null)
    navigate('/login')
  }

  function createUser(payload: { username: string; email: string; role: 'admin' | 'analyst'; password: string }) {
    void createUserRequest(payload).then((createdUser) => {
      setStore((current) => ({ ...current, users: [...current.users, createdUser] }))
    })
  }

  function createCompany(payload: { name: string; sector: string; contact: string; technologies?: string[] }) {
    void createCompanyRequest(payload).then((createdCompany) => {
      setStore((current) => ({ ...current, companies: [...current.companies, createdCompany] }))
    })
  }

  function updateCompany(id: number, company: CompanySummary) {
    setStore((current) => ({
      ...current,
      companies: current.companies.map((item) => (item.id === id ? company : item)),
      vulnerabilities: current.vulnerabilities.map((item) =>
        item.company_id === id ? { ...item, company: company } : item,
      ),
    }))
  }

  function toggleActive(userId: number) {
    const current = store.users.find((user) => user.id === userId)
    if (!current) return
    void updateUserRequest(userId, { active: !current.active }).then((updatedUser) => {
      setStore((state) => ({
        ...state,
        users: state.users.map((user) => (user.id === userId ? updatedUser : user)),
      }))
    })
  }

  function createVulnerability(payload: Omit<Vulnerability, 'id' | 'created_at' | 'updated_at' | 'company'>) {
    void createVulnerabilityRequest(payload).then((createdVulnerability) => {
      setStore((current) => ({
        ...current,
        vulnerabilities: [createdVulnerability, ...current.vulnerabilities],
      }))
    })
  }

  function updateVulnerability(id: number, payload: Partial<Vulnerability>) {
    void updateVulnerabilityRequest(id, payload).then((updatedVulnerability) => {
      setStore((current) => ({
        ...current,
        vulnerabilities: current.vulnerabilities.map((item) => (item.id === id ? updatedVulnerability : item)),
      }))
    })
  }

  function handleDeleteVulnerability(id: number) {
    void deleteVulnerabilityRequest(id).then(() => {
      setStore((current) => ({
        ...current,
        vulnerabilities: current.vulnerabilities.filter((item) => item.id !== id),
      }))
    })
  }

  const currentUser = store.users.find((user) => user.id === sessionUser?.id) || null

  if (!sessionUser) {
    return <LoginPage onLogin={handleLogin} error={error} />
  }

  const emptyStats: DashboardStats = { critical: 0, pending: 0, resolved: 0, active_users: 0, severity_counts: {}, status_counts: {}, analyst_activity: [], irc_distribution: {} }

  return (
    <Layout sessionUser={sessionUser} onLogout={handleLogout}>
      {loading ? <div className="mb-4 rounded-2xl bg-white p-4 text-sm text-slate-500 shadow-soft">Cargando datos...</div> : null}
      {error ? <div className="mb-4 rounded-2xl bg-rose-50 p-4 text-sm text-rose-700 shadow-soft">{error}</div> : null}
      <Routes>
        <Route path="/" element={<DashboardPage role={sessionUser.role} sessionUser={sessionUser} vulnerabilities={store.vulnerabilities} users={store.users} stats={store.stats || emptyStats} />} />
        <Route path="/inicio" element={<DashboardPage role={sessionUser.role} sessionUser={sessionUser} vulnerabilities={store.vulnerabilities} users={store.users} stats={store.stats || emptyStats} />} />
        <Route path="/vulnerabilidades" element={<VulnerabilitiesPage role={sessionUser.role} sessionUserId={sessionUser.id} users={store.users} companies={store.companies} vulnerabilities={store.vulnerabilities} onCreateVulnerability={createVulnerability} onDeleteVulnerability={handleDeleteVulnerability} />} />
        <Route path="/vulnerabilidades/:id" element={<VulnerabilityDetailPage role={sessionUser.role} sessionUser={{ id: sessionUser.id, username: sessionUser.username, email: '', role: sessionUser.role, active: true, latest_activity: '' }} users={store.users} vulnerabilities={store.vulnerabilities} onUpdateVulnerability={updateVulnerability} />} />
        <Route path="/empresas" element={<ProtectedRoute requiredRole="admin"><CompaniesPage companies={store.companies} users={store.users} onCreateCompany={createCompany} /></ProtectedRoute>} />
        <Route path="/empresas/:id" element={<ProtectedRoute requiredRole="admin"><CompanyDetailPage companies={store.companies} users={store.users} vulnerabilities={store.vulnerabilities} onUpdateCompany={updateCompany} /></ProtectedRoute>} />
        <Route path="/estadisticas" element={<ProtectedRoute requiredRole="admin"><StatisticsPage stats={store.stats || emptyStats} /></ProtectedRoute>} />
        <Route path="/equipo" element={<ProtectedRoute requiredRole="admin"><TeamPage users={store.users} /></ProtectedRoute>} />
        <Route path="/equipo/:id" element={<ProtectedRoute requiredRole="admin"><TeamDetailPage users={store.users} vulnerabilities={store.vulnerabilities} /></ProtectedRoute>} />
        <Route path="/usuarios" element={<ProtectedRoute requiredRole="admin"><UsersPage users={store.users} onToggleActive={toggleActive} onCreateUser={createUser} /></ProtectedRoute>} />
        <Route path="*" element={sessionUser ? <DashboardPage role={sessionUser.role} sessionUser={sessionUser} vulnerabilities={store.vulnerabilities} users={store.users} stats={store.stats || emptyStats} /> : null} />
      </Routes>
    </Layout>
  )
}
