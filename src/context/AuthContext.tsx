import React, { createContext, useState, useContext, ReactNode } from 'react'
import { Usuario, UserRole } from '../models/tipos'

interface AuthContextType {
  user: Usuario | null
  isLoggedIn: boolean
  role: UserRole | null
  login: (username: string, password: string) => boolean
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Mock users database
const MOCK_USERS: Record<string, { password: string; user: Usuario }> = {
  admin: {
    password: 'contraseña123',
    user: {
      id: 1,
      username: 'admin',
      role: 'admin',
      company_id: 1,
      active: true
    }
  },
  analyst: {
    password: 'contraseña123',
    user: {
      id: 2,
      username: 'analyst',
      role: 'analyst',
      company_id: 1,
      active: true
    }
  }
}

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<Usuario | null>(null)

  const login = (username: string, password: string): boolean => {
    const mockUser = MOCK_USERS[username]
    
    if (mockUser && mockUser.password === password) {
      setUser(mockUser.user)
      return true
    }
    
    return false
  }

  const logout = () => {
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{
      user,
      isLoggedIn: user !== null,
      role: user?.role || null,
      login,
      logout
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de AuthProvider')
  }
  return context
}
