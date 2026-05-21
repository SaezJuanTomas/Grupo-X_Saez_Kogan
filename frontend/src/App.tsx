import { useEffect, useMemo, useState } from 'react'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { Layout } from './components/Layout'
import { DashboardPage } from './pages/DashboardPage'
import { LoginPage } from './pages/LoginPage'
import { StatisticsPage } from './pages/StatisticsPage'
import { TeamPage } from './pages/TeamPage'
import { UsersPage } from './pages/UsersPage'
import { CompaniesPage } from './pages/CompaniesPage'
import { CompanyDetailPage } from './pages/CompanyDetailPage'
import { VulnerabilitiesPage } from './pages/VulnerabilitiesPage'
import { VulnerabilityDetailPage } from './pages/VulnerabilityDetailPage'
import { createCompany as createCompanyRequest, createUser as createUserRequest, createVulnerability as createVulnerabilityRequest, getComments, getCompanies, getHistory, getStats, getUsers, getVulnerabilities, updateUser as updateUserRequest, updateVulnerability as updateVulnerabilityRequest } from './lib/api'
import { mockSessionUsers, mockUsers } from './data/mockData'
import type { Comment, CompanySummary, DashboardStats, HistoryLog, SessionUser, User, Vulnerability } from './types'

type Store = {
  users: User[]
  companies: CompanySummary[]
  vulnerabilities: Vulnerability[]
  comments: Comment[]
  history: HistoryLog[]
  stats: DashboardStats | null
}

const defaultStore: Store = {
  users: mockUsers,
  companies: [],
  vulnerabilities: [],
  comments: [],
  history: [],
  stats: null,
}

function loadSession(): SessionUser | null {
  const raw = localStorage.getItem('grupo-x-session')
  return raw ? (JSON.parse(raw) as SessionUser) : null
}

export function App() {
  const navigate = useNavigate()
  const location = useLocation()
  const [sessionUser, setSessionUser] = useState<SessionUser | null>(() => loadSession())
  const [error, setError] = useState<string | null>(null)
  const [store, setStore] = useState<Store>(defaultStore)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!sessionUser) return
    const currentSession = sessionUser as SessionUser
    let mounted = true

    async function fetchData() {
      setLoading(true)
      const [users, companies, vulnerabilities, stats] = await Promise.all([
        getUsers(),
        getCompanies(),
        getVulnerabilities(currentSession.role, currentSession.role === 'analyst' ? currentSession.id : undefined),
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
        setLoading(false)
      }
    }

    fetchData().catch(() => setLoading(false))

    return () => {
      mounted = false
    }
  }, [sessionUser, location.pathname])

  useEffect(() => {
    if (!sessionUser) {
      localStorage.removeItem('grupo-x-session')
      return
    }
    localStorage.setItem('grupo-x-session', JSON.stringify(sessionUser))
  }, [sessionUser])

  function login(username: string, password: string) {
    const user = mockSessionUsers.find((item) => item.username === username && item.password === password)
    if (!user) {
      setError('Credenciales inválidas')
      return
    }

    setError(null)
    setSessionUser({ id: user.id, username: user.username, role: user.role })
    navigate('/')
  }

  function logout() {
    setSessionUser(null)
    setStore(defaultStore)
    navigate('/login')
  }

  function createUser(payload: { username: string; email: string; role: 'admin' | 'analyst'; password: string }) {
    void createUserRequest(payload).then((createdUser) => {
      setStore((current) => ({ ...current, users: [...current.users, createdUser] }))
    })
  }

  function createCompany(payload: { name: string; sector: string; contact: string }) {
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

  const currentUser = useMemo(() => store.users.find((user) => user.id === sessionUser?.id) || null, [store.users, sessionUser])

  if (!sessionUser) {
    return <LoginPage onLogin={login} error={error} />
  }

  const emptyStats: DashboardStats = { critical: 0, pending: 0, resolved: 0, active_users: 0, severity_counts: {}, status_counts: {}, analyst_activity: [], irc_distribution: {} }

  return (
    <Layout sessionUser={sessionUser} onLogout={logout}>
      {loading ? <div className="mb-4 rounded-2xl bg-white p-4 text-sm text-slate-500 shadow-soft">Cargando datos...</div> : null}
      <Routes>
        <Route path="/" element={<DashboardPage role={sessionUser.role} sessionUser={sessionUser} vulnerabilities={store.vulnerabilities} users={store.users} stats={store.stats || emptyStats} />} />
        <Route path="/inicio" element={<DashboardPage role={sessionUser.role} sessionUser={sessionUser} vulnerabilities={store.vulnerabilities} users={store.users} stats={store.stats || emptyStats} />} />
        <Route path="/vulnerabilidades" element={<VulnerabilitiesPage role={sessionUser.role} sessionUserId={sessionUser.id} users={store.users} companies={store.companies} vulnerabilities={store.vulnerabilities} onCreateVulnerability={createVulnerability} />} />
        <Route path="/vulnerabilidades/:id" element={<VulnerabilityDetailPage role={sessionUser.role} sessionUser={currentUser || { id: sessionUser.id, username: sessionUser.username, email: '', role: sessionUser.role, active: true, latest_activity: '' }} users={store.users} vulnerabilities={store.vulnerabilities} comments={store.comments} history={store.history} onRefresh={() => window.location.reload()} onUpdateVulnerability={updateVulnerability} />} />
        <Route path="/empresas" element={sessionUser.role === 'admin' ? <CompaniesPage companies={store.companies} users={store.users} onCreateCompany={createCompany} /> : <Navigate to="/" replace />} />
        <Route path="/empresas/:id" element={sessionUser.role === 'admin' ? <CompanyDetailPage companies={store.companies} users={store.users} vulnerabilities={store.vulnerabilities} onUpdateCompany={updateCompany} /> : <Navigate to="/" replace />} />
        <Route path="/estadisticas" element={sessionUser.role === 'admin' ? <StatisticsPage stats={store.stats || emptyStats} /> : <Navigate to="/" replace />} />
        <Route path="/equipo" element={sessionUser.role === 'admin' ? <TeamPage users={store.users} /> : <Navigate to="/" replace />} />
        <Route path="/usuarios" element={sessionUser.role === 'admin' ? <UsersPage users={store.users} onToggleActive={toggleActive} onCreateUser={createUser} /> : <Navigate to="/" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}
