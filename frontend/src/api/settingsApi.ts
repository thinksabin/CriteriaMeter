export interface AuthSettings {
  signup_enabled:       boolean
  min_password_length:  number
  require_number:       boolean
  require_uppercase:    boolean
  require_special_char: boolean
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch('/api/admin' + path, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (res.status === 401) {
    window.location.href = '/login'
    return undefined as unknown as T
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error((body as { detail?: string }).detail ?? `HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

export const settingsApi = {
  getAuthSettings: (): Promise<AuthSettings> =>
    req('/auth-settings'),

  updateAuthSettings: (data: Partial<AuthSettings>): Promise<AuthSettings> =>
    req('/auth-settings', { method: 'PATCH', body: JSON.stringify(data) }),
}
