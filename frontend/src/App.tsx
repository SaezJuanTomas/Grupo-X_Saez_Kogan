import { useEffect, useState, useCallback, type ReactNode } from 'react'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Layout } from './components/Layout'
import { Toast, ToastError } from './components/Ui'
import { LoginPage } from './pages/LoginPage'
import { LandingPage } from './pages/LandingPage'
import { DashboardPage } from './pages/DashboardPage'
import { StatisticsPage } from './pages/StatisticsPage'
import { TeamPage } from './pages/TeamPage'
import { TeamDetailPage } from './pages/TeamDetailPage'
import { UsersPage } from './pages/UsersPage'
import { CompaniesPage } from './pages/CompaniesPage'
import { CompanyDetailPage } from './pages/CompanyDetailPage'
import { VulnerabilitiesPage } from './pages/VulnerabilitiesPage'
import { VulnerabilityDetailPage } from './pages/VulnerabilityDetailPage'
import { createCompany as createCompanyRequest, createUser as createUserRequest, createVulnerability as createVulnerabilityRequest, deleteVulnerability as deleteVulnerabilityRequest, getComments, getCompanies, getHistory, getStats, getUsers, getVulnerabilities, reactivateCompany as reactivateCompanyRequest, softDeleteCompany as softDeleteCompanyRequest, updateUser as updateUserRequest, updateVulnerability as updateVulnerabilityRequest } from './lib/api'
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
  const [toast, setToast] = useState<string | null>(null)
  const [toastError, setToastError] = useState<string | null>(null)

  useEffect(() => {
    if (!sessionUser) return
    const currentUser = sessionUser
    let mounted = true

    async function fetchData() {
      const isInitialLoad = store.companies.length === 0
      if (isInitialLoad) setLoading(true)
      try {
        const [users, companies, vulnerabilities, stats] = await Promise.all([
          currentUser.role === 'admin' ? getUsers() : Promise.resolve([] as User[]),
          getCompanies(true),
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

  const refreshData = useCallback(async () => {
    if (!sessionUser) return
    try {
      const [users, companies, vulnerabilities, stats] = await Promise.all([
        sessionUser.role === 'admin' ? getUsers() : Promise.resolve([] as User[]),
        getCompanies(true),
        getVulnerabilities(sessionUser.role, sessionUser.role === 'analyst' ? sessionUser.id : undefined),
        getStats(),
      ])
      setStore((current) => ({ ...current, users, companies, vulnerabilities, stats }))
    } catch {
      // silent
    }
  }, [sessionUser])

  function showToast(message: string) {
    setToast(message)
    setTimeout(() => setToast(null), 3000)
  }

  function showError(message: string) {
    setToastError(message)
    setTimeout(() => setToastError(null), 4000)
  }

  async function handleLogin(username: string, password: string) {
    try {
      await login(username, password)
      setError(null)
      navigate('/inicio')
    } catch {
      setError('Nombre de usuario o contraseña incorrectos')
    }
  }

  async function handleLogout() {
    await logout()
    setStore(defaultStore)
    setError(null)
    navigate('/login')
  }

  async function createUser(payload: { username: string; email: string; role: 'admin' | 'analyst'; password: string }) {
    try {
      const createdUser = await createUserRequest(payload)
      setStore((current) => ({ ...current, users: [...current.users, createdUser] }))
      showToast('Usuario creado correctamente')
    } catch (err: any) {
      const msg = err?.response?.data?.error?.message || 'Error al crear usuario'
      showError(msg)
    }
  }

  async function createCompany(payload: { name: string; sector: string; contact: string; technologies?: string[] }) {
    try {
      const createdCompany = await createCompanyRequest(payload)
      setStore((current) => ({ ...current, companies: [...current.companies, createdCompany] }))
      showToast('Empresa creada correctamente')
    } catch (err: any) {
      const msg = err?.response?.data?.error?.message || 'Error al crear empresa'
      showError(msg)
    }
  }

  async function updateCompany(id: number, company: CompanySummary) {
    setStore((current) => ({
      ...current,
      companies: current.companies.map((item) => (item.id === id ? company : item)),
      vulnerabilities: current.vulnerabilities.map((item) =>
        item.company_id === id ? { ...item, company: company } : item,
      ),
    }))
    showToast('Cambios guardados')
  }

  async function toggleActive(userId: number) {
    const current = store.users.find((user) => user.id === userId)
    if (!current) return
    try {
      const updatedUser = await updateUserRequest(userId, { active: !current.active })
      setStore((state) => ({
        ...state,
        users: state.users.map((user) => (user.id === userId ? updatedUser : user)),
      }))
      showToast(current.active ? 'Usuario desactivado' : 'Usuario reactivado')
    } catch (err: any) {
      const msg = err?.response?.data?.error?.message || 'Error al actualizar usuario'
      showError(msg)
    }
  }

  function extractApiError(err: any, fallback: string): string {
    const data = err?.response?.data
    if (data?.error?.message) return data.error.message
    if (typeof data?.detail === 'string') return data.detail
    if (Array.isArray(data?.detail)) {
      const first = data.detail[0]
      return first?.msg ? `${first.msg}${first.loc ? ` (${first.loc.join('.')})` : ''}` : fallback
    }
    return fallback
  }

  async function createVulnerability(payload: Omit<Vulnerability, 'id' | 'created_at' | 'updated_at' | 'company'>): Promise<boolean> {
    try {
      await createVulnerabilityRequest(payload)
      await refreshData()
      showToast(`Vulnerabilidad ${payload.cve} creada correctamente`)
      return true
    } catch (err: any) {
      showError(extractApiError(err, 'Error al crear vulnerabilidad'))
      return false
    }
  }

  async function updateVulnerability(id: number, payload: Partial<Vulnerability>) {
    const updatedVulnerability = await updateVulnerabilityRequest(id, payload)
    setStore((current) => ({
      ...current,
      vulnerabilities: current.vulnerabilities.map((item) => (item.id === id ? updatedVulnerability : item)),
    }))
    showToast('Cambios guardados')
  }

  async function handleDeleteVulnerability(id: number) {
    try {
      await deleteVulnerabilityRequest(id)
      setStore((current) => ({
        ...current,
        vulnerabilities: current.vulnerabilities.filter((item) => item.id !== id),
      }))
      showToast('Vulnerabilidad eliminada')
    } catch (err: any) {
      const msg = err?.response?.data?.error?.message || 'Error al eliminar vulnerabilidad'
      showError(msg)
    }
  }

  async function handleSoftDeleteCompany(id: number) {
    try {
      const updatedCompany = await softDeleteCompanyRequest(id)
      setStore((current) => ({
        ...current,
        companies: current.companies.map((item) => (item.id === id ? updatedCompany : item)),
      }))
      showToast('Empresa desactivada')
    } catch (err: any) {
      const msg = err?.response?.data?.error?.message || 'Error al desactivar empresa'
      showError(msg)
    }
  }

  async function handleReactivateCompany(id: number) {
    try {
      const updatedCompany = await reactivateCompanyRequest(id)
      setStore((current) => ({
        ...current,
        companies: current.companies.map((item) => (item.id === id ? updatedCompany : item)),
      }))
      showToast('Empresa reactivada')
    } catch (err: any) {
      const msg = err?.response?.data?.error?.message || 'Error al reactivar empresa'
      showError(msg)
    }
  }

  const emptyStats: DashboardStats = { critical: 0, pending: 0, resolved: 0, active_users: 0, severity_counts: {}, status_counts: {}, analyst_activity: [], irc_distribution: {} }

  const toasts = (
    <>
      {toast ? <Toast message={toast} onClose={() => setToast(null)} /> : null}
      {toastError ? <ToastError message={toastError} onClose={() => setToastError(null)} /> : null}
    </>
  )

  if (!sessionUser) {
    return (
      <>
        <Routes>
          <Route path="/" element={<LandingPage onLogout={handleLogout} />} />
          <Route path="/login" element={<LoginPage onLogin={handleLogin} error={error} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        {toasts}
      </>
    )
  }

  const authedUser = sessionUser

  function page(node: ReactNode) {
    return (
      <Layout sessionUser={authedUser} onLogout={handleLogout}>
        {loading && store.companies.length === 0 ? <div className="mb-4 rounded-2xl bg-white p-4 text-sm text-slate-500 shadow-soft">Cargando datos...</div> : null}
        {error ? <div className="mb-4 rounded-2xl bg-rose-50 p-4 text-sm text-rose-700 shadow-soft">{error}</div> : null}
        {node}
      </Layout>
    )
  }

  return (
    <>
      <Routes>
        <Route path="/" element={<LandingPage onLogout={handleLogout} />} />
        <Route path="/login" element={<Navigate to="/inicio" replace />} />
        <Route path="/inicio" element={page(<DashboardPage role={sessionUser.role} sessionUser={sessionUser} vulnerabilities={store.vulnerabilities} users={store.users} stats={store.stats || emptyStats} />)} />
        <Route path="/vulnerabilidades" element={page(<ProtectedRoute><VulnerabilitiesPage role={sessionUser.role} sessionUserId={sessionUser.id} users={store.users} companies={store.companies.filter((c) => c.is_active !== false)} vulnerabilities={store.vulnerabilities} onCreateVulnerability={createVulnerability} onDeleteVulnerability={handleDeleteVulnerability} /></ProtectedRoute>)} />
        <Route path="/vulnerabilidades/:id" element={page(<ProtectedRoute><VulnerabilityDetailPage role={sessionUser.role} sessionUser={{ id: sessionUser.id, username: sessionUser.username, email: '', role: sessionUser.role, active: true, latest_activity: '' }} users={store.users} vulnerabilities={store.vulnerabilities} onUpdateVulnerability={updateVulnerability} onRefresh={refreshData} /></ProtectedRoute>)} />
        <Route path="/empresas" element={page(<ProtectedRoute requiredRole="admin"><CompaniesPage companies={store.companies} users={store.users} vulnerabilities={store.vulnerabilities} onCreateCompany={createCompany} onSoftDeleteCompany={handleSoftDeleteCompany} onReactivateCompany={handleReactivateCompany} /></ProtectedRoute>)} />
        <Route path="/empresas/:id" element={page(<ProtectedRoute requiredRole="admin"><CompanyDetailPage companies={store.companies.filter((c) => c.is_active !== false)} users={store.users} vulnerabilities={store.vulnerabilities} onUpdateCompany={updateCompany} /></ProtectedRoute>)} />
        <Route path="/estadisticas" element={page(<ProtectedRoute requiredRole="admin"><StatisticsPage stats={store.stats || emptyStats} /></ProtectedRoute>)} />
        <Route path="/equipo" element={page(<ProtectedRoute requiredRole="admin"><TeamPage users={store.users} /></ProtectedRoute>)} />
        <Route path="/equipo/:id" element={page(<ProtectedRoute requiredRole="admin"><TeamDetailPage users={store.users} vulnerabilities={store.vulnerabilities} /></ProtectedRoute>)} />
        <Route path="/usuarios" element={page(<ProtectedRoute requiredRole="admin"><UsersPage users={store.users} onToggleActive={toggleActive} onCreateUser={createUser} /></ProtectedRoute>)} />
        <Route path="*" element={<Navigate to="/inicio" replace />} />
      </Routes>
      {toasts}
    </>
  )
}
