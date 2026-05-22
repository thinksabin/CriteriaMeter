const BASE = '/api/auth'

export interface AuthUser {
  id: string
  email: string
  first_name: string
  last_name: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: AuthUser
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

async function request<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data?.detail ?? `HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

export const authApi = {
  signup: (data: SignupRequest): Promise<AuthUser> =>
    request('/signup', data),

  login: (data: LoginRequest): Promise<LoginResponse> =>
    request('/login', data),
}
