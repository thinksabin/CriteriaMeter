const BASE = '/api/auth'

export interface AuthUser {
  id: string
  email: string
  first_name: string
  last_name: string
  roles: string[]
}

interface SignupRequest {
  first_name: string
  last_name: string
  email: string
  password: string
  mobile_number?: string
}

interface LoginRequest {
  email: string
  password: string
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error((data as { detail?: string }).detail ?? `HTTP ${res.status}`)
  }
  if (res.status === 204) return undefined as unknown as T
  return res.json() as Promise<T>
}

export const authApi = {
  signup: (data: SignupRequest): Promise<AuthUser> =>
    request('/signup', { method: 'POST', body: JSON.stringify(data) }),

  login: (data: LoginRequest): Promise<AuthUser> =>
    request('/login', { method: 'POST', body: JSON.stringify(data) }),

  me: (): Promise<AuthUser> =>
    request('/me', { method: 'GET' }),

  logout: (): Promise<void> =>
    request('/logout', { method: 'POST' }),

  changePassword: (data: { current_password: string; new_password: string; confirm_password: string }): Promise<void> =>
    request('/change-password', { method: 'POST', body: JSON.stringify(data) }),
}
