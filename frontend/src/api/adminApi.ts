const BASE = '/api/admin'

export interface AdminUser {
  id: string
  first_name: string
  last_name: string
  email: string
  mobile_number: string | null
  is_active: boolean
  api_access: boolean
  email_verified: boolean
  last_login_at: string | null
  created_at: string
  roles: string[]
  groups: string[]
}

export interface AdminRole {
  id: number
  name: string
  description: string | null
  user_count: number
}

export interface AdminGroup {
  id: number
  name: string
  description: string | null
  roles: string[]
  member_count: number
  created_at: string
}

interface UserCreatePayload {
  first_name: string
  last_name: string
  email: string
  password: string
  mobile_number?: string
}

interface UserUpdatePayload {
  first_name?: string
  last_name?: string
  email?: string
  mobile_number?: string | null
}

interface RoleCreatePayload {
  name: string
  description?: string
}

interface RoleUpdatePayload {
  name?: string
  description?: string | null
}

interface GroupCreatePayload {
  name: string
  description?: string
}

interface GroupUpdatePayload {
  name?: string
  description?: string | null
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error((body as { detail?: string }).detail ?? `HTTP ${res.status}`)
  }
  if (res.status === 204) return undefined as unknown as T
  return res.json() as Promise<T>
}

export const adminApi = {
  // Users
  listUsers: (): Promise<AdminUser[]> =>
    req('/users'),

  createUser: (data: UserCreatePayload): Promise<AdminUser> =>
    req('/users', { method: 'POST', body: JSON.stringify(data) }),

  updateUser: (id: string, data: UserUpdatePayload): Promise<AdminUser> =>
    req(`/users/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),

  deleteUser: (id: string): Promise<void> =>
    req(`/users/${id}`, { method: 'DELETE' }),

  toggleActive: (id: string): Promise<AdminUser> =>
    req(`/users/${id}/toggle-active`, { method: 'PATCH' }),

  toggleApiAccess: (id: string): Promise<AdminUser> =>
    req(`/users/${id}/toggle-api`, { method: 'PATCH' }),

  // Direct role assignment (user ↔ role)
  assignRole: (userId: string, roleId: number): Promise<void> =>
    req(`/users/${userId}/roles/${roleId}`, { method: 'PUT' }),

  revokeRole: (userId: string, roleId: number): Promise<void> =>
    req(`/users/${userId}/roles/${roleId}`, { method: 'DELETE' }),

  // Group membership from user side (user ↔ group)
  addUserToGroup: (userId: string, groupId: number): Promise<void> =>
    req(`/users/${userId}/groups/${groupId}`, { method: 'PUT' }),

  removeUserFromGroup: (userId: string, groupId: number): Promise<void> =>
    req(`/users/${userId}/groups/${groupId}`, { method: 'DELETE' }),

  // Roles
  listRoles: (): Promise<AdminRole[]> =>
    req('/roles'),

  createRole: (data: RoleCreatePayload): Promise<AdminRole> =>
    req('/roles', { method: 'POST', body: JSON.stringify(data) }),

  updateRole: (id: number, data: RoleUpdatePayload): Promise<AdminRole> =>
    req(`/roles/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),

  deleteRole: (id: number): Promise<void> =>
    req(`/roles/${id}`, { method: 'DELETE' }),

  // Groups
  listGroups: (): Promise<AdminGroup[]> =>
    req('/groups'),

  createGroup: (data: GroupCreatePayload): Promise<AdminGroup> =>
    req('/groups', { method: 'POST', body: JSON.stringify(data) }),

  updateGroup: (id: number, data: GroupUpdatePayload): Promise<AdminGroup> =>
    req(`/groups/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),

  deleteGroup: (id: number): Promise<void> =>
    req(`/groups/${id}`, { method: 'DELETE' }),

  // Group role assignment (group ↔ role)
  assignGroupRole: (groupId: number, roleId: number): Promise<void> =>
    req(`/groups/${groupId}/roles/${roleId}`, { method: 'PUT' }),

  revokeGroupRole: (groupId: number, roleId: number): Promise<void> =>
    req(`/groups/${groupId}/roles/${roleId}`, { method: 'DELETE' }),

  // Group member management from group side (group ↔ user)
  addGroupMember: (groupId: number, userId: string): Promise<void> =>
    req(`/groups/${groupId}/members/${userId}`, { method: 'PUT' }),

  removeGroupMember: (groupId: number, userId: string): Promise<void> =>
    req(`/groups/${groupId}/members/${userId}`, { method: 'DELETE' }),
}
