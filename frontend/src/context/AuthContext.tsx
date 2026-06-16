import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import { login as apiLogin, logout as apiLogout, setToken } from '../lib/api'
import type { SessionUser } from '../types'

type AuthContextType = {
  user: SessionUser | null
  error: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

function loadSession(): SessionUser | null {
  try {
    const raw = localStorage.getItem('grupo-x-session')
    return raw ? (JSON.parse(raw) as SessionUser) : null
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<SessionUser | null>(() => loadSession())
  const [error, setError] = useState<string | null>(null)

  const login = useCallback(async (username: string, password: string) => {
    try {
      const result = await apiLogin({ username, password })
      setToken(result.access_token)
      setError(null)
      const sessionUser: SessionUser = { id: result.user_id, username: result.username, role: result.role as 'admin' | 'analyst' }
      localStorage.setItem('grupo-x-session', JSON.stringify(sessionUser))
      setUser(sessionUser)
    } catch {
      setError('Credenciales inválidas')
    }
  }, [])

  const logout = useCallback(async () => {
    await apiLogout()
    setToken(null)
    localStorage.removeItem('grupo-x-session')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, error, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
