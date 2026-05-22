import { createContext, useContext, useState, type ReactNode } from 'react'
import type { AuthUser } from '../api/authApi'

interface AuthContextValue {
  user: AuthUser | null
  token: string | null
  isAuthenticated: boolean
  login: (token: string, user: AuthUser) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

function loadFromStorage(): { token: string | null; user: AuthUser | null } {
  try {
    const token = localStorage.getItem('cm_token')
    const raw = localStorage.getItem('cm_user')
    const user = raw ? (JSON.parse(raw) as AuthUser) : null
    return { token, user }
  } catch {
    return { token: null, user: null }
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const stored = loadFromStorage()
  const [token, setToken] = useState<string | null>(stored.token)
  const [user, setUser]   = useState<AuthUser | null>(stored.user)

  function login(newToken: string, newUser: AuthUser) {
    localStorage.setItem('cm_token', newToken)
    localStorage.setItem('cm_user', JSON.stringify(newUser))
    setToken(newToken)
    setUser(newUser)
  }

  function logout() {
    localStorage.removeItem('cm_token')
    localStorage.removeItem('cm_user')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!token, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
