import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { authApi, type AuthUser } from '../api/authApi'

function hasSessionCookie(): boolean {
  return document.cookie.split(';').some(c => c.trim().startsWith('cm_present='))
}

interface AuthContextValue {
  user: AuthUser | null
  isAuthenticated: boolean
  isAdmin: boolean
  login: (user: AuthUser) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser]       = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Remove legacy localStorage tokens left from the pre-cookie implementation
    localStorage.removeItem('cm_token')
    localStorage.removeItem('cm_user')

    if (!hasSessionCookie()) {
      // No presence cookie → definitely not logged in; skip the network round-trip
      setLoading(false)
      return
    }

    authApi.me()
      .then(u => setUser(u))
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [])

  function login(newUser: AuthUser) {
    setUser(newUser)
  }

  function logout() {
    authApi.logout().finally(() => setUser(null))
  }

  const isAdmin = user?.roles.includes('admin') ?? false

  if (loading) return null

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isAdmin, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
