import { useCallback, useEffect, useState } from 'react'
import { AdminGroup, AdminRole, AdminUser, adminApi } from '../../api/adminApi'

// ── Local types ────────────────────────────────────────────────────────────────

type Tab = 'users' | 'roles' | 'groups'

interface UserForm {
  first_name: string; last_name: string
  email: string; mobile_number: string; password: string
}

interface RoleForm  { name: string; description: string }
interface GroupForm { name: string; description: string }

const EMPTY_USER_FORM:  UserForm  = { first_name: '', last_name: '', email: '', mobile_number: '', password: '' }
const EMPTY_ROLE_FORM:  RoleForm  = { name: '', description: '' }
const EMPTY_GROUP_FORM: GroupForm = { name: '', description: '' }

// ── Component ──────────────────────────────────────────────────────────────────

export default function UserManagement() {
  const [tab, setTab] = useState<Tab>('users')

  // Data
  const [users,  setUsers]  = useState<AdminUser[]>([])
  const [roles,  setRoles]  = useState<AdminRole[]>([])
  const [groups, setGroups] = useState<AdminGroup[]>([])
  const [loading, setLoading]   = useState(true)
  const [pageError, setPageError] = useState<string | null>(null)

  // ── User modal ────────────────────────────────────────────────────────────────
  const [userModalOpen, setUserModalOpen] = useState(false)
  const [editingUser,   setEditingUser]   = useState<AdminUser | null>(null)
  const [userForm,      setUserForm]      = useState<UserForm>(EMPTY_USER_FORM)
  const [userFormErr,   setUserFormErr]   = useState<string | null>(null)
  const [savingUser,    setSavingUser]    = useState(false)

  // ── Role modal ────────────────────────────────────────────────────────────────
  const [roleModalOpen, setRoleModalOpen] = useState(false)
  const [editingRole,   setEditingRole]   = useState<AdminRole | null>(null)
  const [roleForm,      setRoleForm]      = useState<RoleForm>(EMPTY_ROLE_FORM)
  const [roleFormErr,   setRoleFormErr]   = useState<string | null>(null)
  const [savingRole,    setSavingRole]    = useState(false)

  // ── Group modal (add/edit) ────────────────────────────────────────────────────
  const [groupModalOpen, setGroupModalOpen] = useState(false)
  const [editingGroup,   setEditingGroup]   = useState<AdminGroup | null>(null)
  const [groupForm,      setGroupForm]      = useState<GroupForm>(EMPTY_GROUP_FORM)
  const [groupFormErr,   setGroupFormErr]   = useState<string | null>(null)
  const [savingGroup,    setSavingGroup]    = useState(false)

  // ── Assign roles to user ──────────────────────────────────────────────────────
  const [assignRolesUser,  setAssignRolesUser]  = useState<AdminUser | null>(null)
  const [assignedRoleIds,  setAssignedRoleIds]  = useState<Set<number>>(new Set())
  const [savingAssignRoles, setSavingAssignRoles] = useState(false)

  // ── Assign groups to user ─────────────────────────────────────────────────────
  const [assignGroupsUser,  setAssignGroupsUser]  = useState<AdminUser | null>(null)
  const [assignedGroupIds,  setAssignedGroupIds]  = useState<Set<number>>(new Set())
  const [savingAssignGroups, setSavingAssignGroups] = useState(false)

  // ── Assign roles to group ─────────────────────────────────────────────────────
  const [assignGroupRolesTarget, setAssignGroupRolesTarget] = useState<AdminGroup | null>(null)
  const [groupRoleIds,           setGroupRoleIds]           = useState<Set<number>>(new Set())
  const [savingGroupRoles,       setSavingGroupRoles]       = useState(false)

  // ── Manage group members ──────────────────────────────────────────────────────
  const [manageMembersGroup, setManageMembersGroup] = useState<AdminGroup | null>(null)
  const [memberIds,          setMemberIds]          = useState<Set<string>>(new Set())
  const [savingMembers,      setSavingMembers]      = useState(false)

  // ── Data loading ──────────────────────────────────────────────────────────────

  const fetchAll = useCallback(async () => {
    setLoading(true)
    setPageError(null)
    try {
      const [u, r, g] = await Promise.all([
        adminApi.listUsers(),
        adminApi.listRoles(),
        adminApi.listGroups(),
      ])
      setUsers(u); setRoles(r); setGroups(g)
    } catch (e) {
      setPageError(e instanceof Error ? e.message : 'Failed to load data.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { void fetchAll() }, [fetchAll])

  // ── User CRUD ─────────────────────────────────────────────────────────────────

  function openAddUser() {
    setEditingUser(null); setUserForm(EMPTY_USER_FORM); setUserFormErr(null); setUserModalOpen(true)
  }
  function openEditUser(u: AdminUser) {
    setEditingUser(u)
    setUserForm({ first_name: u.first_name, last_name: u.last_name, email: u.email,
                  mobile_number: u.mobile_number ?? '', password: '' })
    setUserFormErr(null); setUserModalOpen(true)
  }
  async function saveUser() {
    setUserFormErr(null)
    if (!userForm.first_name.trim() || !userForm.last_name.trim() || !userForm.email.trim()) {
      setUserFormErr('First name, last name, and email are required.'); return
    }
    if (!editingUser && userForm.password.length < 8) {
      setUserFormErr('Password must be at least 8 characters.'); return
    }
    setSavingUser(true)
    try {
      if (editingUser) {
        const up = await adminApi.updateUser(editingUser.id, {
          first_name: userForm.first_name, last_name: userForm.last_name,
          email: userForm.email, mobile_number: userForm.mobile_number || null,
        })
        setUsers(prev => prev.map(u => u.id === up.id ? up : u))
      } else {
        const cr = await adminApi.createUser({
          first_name: userForm.first_name, last_name: userForm.last_name,
          email: userForm.email, password: userForm.password,
          mobile_number: userForm.mobile_number || undefined,
        })
        setUsers(prev => [...prev, cr])
      }
      setUserModalOpen(false)
    } catch (e) { setUserFormErr(e instanceof Error ? e.message : 'Save failed.')
    } finally { setSavingUser(false) }
  }
  async function deleteUser(u: AdminUser) {
    if (!confirm(`Delete user "${u.first_name} ${u.last_name}"? This cannot be undone.`)) return
    try { await adminApi.deleteUser(u.id); setUsers(prev => prev.filter(x => x.id !== u.id)) }
    catch (e) { setPageError(e instanceof Error ? e.message : 'Delete failed.') }
  }
  async function handleToggleActive(u: AdminUser) {
    try { const up = await adminApi.toggleActive(u.id); setUsers(prev => prev.map(x => x.id === up.id ? up : x)) }
    catch (e) { setPageError(e instanceof Error ? e.message : 'Toggle failed.') }
  }
  async function handleToggleApi(u: AdminUser) {
    try { const up = await adminApi.toggleApiAccess(u.id); setUsers(prev => prev.map(x => x.id === up.id ? up : x)) }
    catch (e) { setPageError(e instanceof Error ? e.message : 'Toggle failed.') }
  }
  async function handleResetPassword(u: AdminUser) {
    if (!confirm(`Send a password reset email to ${u.email}?`)) return
    try {
      await adminApi.resetUserPassword(u.id)
      alert(`Password reset email queued for ${u.email}.`)
    } catch (e) { setPageError(e instanceof Error ? e.message : 'Reset failed.') }
  }

  // ── Assign roles to user ──────────────────────────────────────────────────────

  function openAssignRoles(u: AdminUser) {
    const nameToId = new Map(roles.map(r => [r.name, r.id]))
    setAssignedRoleIds(new Set(u.roles.map(n => nameToId.get(n)).filter((id): id is number => id !== undefined)))
    setAssignRolesUser(u)
  }
  async function saveAssignRoles() {
    if (!assignRolesUser) return
    setSavingAssignRoles(true)
    try {
      const nameToId = new Map(roles.map(r => [r.name, r.id]))
      const currentIds = new Set(assignRolesUser.roles.map(n => nameToId.get(n)).filter((id): id is number => id !== undefined))
      await Promise.all([
        ...[...assignedRoleIds].filter(id => !currentIds.has(id)).map(rid => adminApi.assignRole(assignRolesUser.id, rid)),
        ...[...currentIds].filter(id => !assignedRoleIds.has(id)).map(rid => adminApi.revokeRole(assignRolesUser.id, rid)),
      ])
      setUsers(await adminApi.listUsers()); setAssignRolesUser(null)
    } catch (e) { setPageError(e instanceof Error ? e.message : 'Role assignment failed.')
    } finally { setSavingAssignRoles(false) }
  }

  // ── Assign groups to user ─────────────────────────────────────────────────────

  function openAssignGroups(u: AdminUser) {
    const nameToId = new Map(groups.map(g => [g.name, g.id]))
    setAssignedGroupIds(new Set(u.groups.map(n => nameToId.get(n)).filter((id): id is number => id !== undefined)))
    setAssignGroupsUser(u)
  }
  async function saveAssignGroups() {
    if (!assignGroupsUser) return
    setSavingAssignGroups(true)
    try {
      const nameToId = new Map(groups.map(g => [g.name, g.id]))
      const currentIds = new Set(assignGroupsUser.groups.map(n => nameToId.get(n)).filter((id): id is number => id !== undefined))
      await Promise.all([
        ...[...assignedGroupIds].filter(id => !currentIds.has(id)).map(gid => adminApi.addUserToGroup(assignGroupsUser.id, gid)),
        ...[...currentIds].filter(id => !assignedGroupIds.has(id)).map(gid => adminApi.removeUserFromGroup(assignGroupsUser.id, gid)),
      ])
      const [refreshedUsers, refreshedGroups] = await Promise.all([adminApi.listUsers(), adminApi.listGroups()])
      setUsers(refreshedUsers); setGroups(refreshedGroups); setAssignGroupsUser(null)
    } catch (e) { setPageError(e instanceof Error ? e.message : 'Group assignment failed.')
    } finally { setSavingAssignGroups(false) }
  }

  // ── Role CRUD ─────────────────────────────────────────────────────────────────

  function openAddRole() { setEditingRole(null); setRoleForm(EMPTY_ROLE_FORM); setRoleFormErr(null); setRoleModalOpen(true) }
  function openEditRole(r: AdminRole) { setEditingRole(r); setRoleForm({ name: r.name, description: r.description ?? '' }); setRoleFormErr(null); setRoleModalOpen(true) }
  async function saveRole() {
    setRoleFormErr(null)
    if (!roleForm.name.trim()) { setRoleFormErr('Role name is required.'); return }
    setSavingRole(true)
    try {
      if (editingRole) {
        const up = await adminApi.updateRole(editingRole.id, { name: roleForm.name, description: roleForm.description || null })
        setRoles(prev => prev.map(r => r.id === up.id ? up : r))
      } else {
        const cr = await adminApi.createRole({ name: roleForm.name, description: roleForm.description || undefined })
        setRoles(prev => [...prev, cr])
      }
      setRoleModalOpen(false)
    } catch (e) { setRoleFormErr(e instanceof Error ? e.message : 'Save failed.')
    } finally { setSavingRole(false) }
  }
  async function deleteRole(r: AdminRole) {
    if (!confirm(`Delete role "${r.name}"? Users with this role will lose it.`)) return
    try { await adminApi.deleteRole(r.id); setRoles(prev => prev.filter(x => x.id !== r.id)) }
    catch (e) { setPageError(e instanceof Error ? e.message : 'Delete failed.') }
  }

  // ── Group CRUD ────────────────────────────────────────────────────────────────

  function openAddGroup() { setEditingGroup(null); setGroupForm(EMPTY_GROUP_FORM); setGroupFormErr(null); setGroupModalOpen(true) }
  function openEditGroup(g: AdminGroup) { setEditingGroup(g); setGroupForm({ name: g.name, description: g.description ?? '' }); setGroupFormErr(null); setGroupModalOpen(true) }
  async function saveGroup() {
    setGroupFormErr(null)
    if (!groupForm.name.trim()) { setGroupFormErr('Group name is required.'); return }
    setSavingGroup(true)
    try {
      if (editingGroup) {
        const up = await adminApi.updateGroup(editingGroup.id, { name: groupForm.name, description: groupForm.description || null })
        setGroups(prev => prev.map(g => g.id === up.id ? up : g))
      } else {
        const cr = await adminApi.createGroup({ name: groupForm.name, description: groupForm.description || undefined })
        setGroups(prev => [...prev, cr])
      }
      setGroupModalOpen(false)
    } catch (e) { setGroupFormErr(e instanceof Error ? e.message : 'Save failed.')
    } finally { setSavingGroup(false) }
  }
  async function deleteGroup(g: AdminGroup) {
    if (!confirm(`Delete group "${g.name}"? All member assignments will be removed.`)) return
    try { await adminApi.deleteGroup(g.id); setGroups(prev => prev.filter(x => x.id !== g.id)) }
    catch (e) { setPageError(e instanceof Error ? e.message : 'Delete failed.') }
  }

  // ── Assign roles to group ─────────────────────────────────────────────────────

  function openAssignGroupRoles(g: AdminGroup) {
    const nameToId = new Map(roles.map(r => [r.name, r.id]))
    setGroupRoleIds(new Set(g.roles.map(n => nameToId.get(n)).filter((id): id is number => id !== undefined)))
    setAssignGroupRolesTarget(g)
  }
  async function saveAssignGroupRoles() {
    if (!assignGroupRolesTarget) return
    setSavingGroupRoles(true)
    try {
      const nameToId = new Map(roles.map(r => [r.name, r.id]))
      const currentIds = new Set(assignGroupRolesTarget.roles.map(n => nameToId.get(n)).filter((id): id is number => id !== undefined))
      await Promise.all([
        ...[...groupRoleIds].filter(id => !currentIds.has(id)).map(rid => adminApi.assignGroupRole(assignGroupRolesTarget.id, rid)),
        ...[...currentIds].filter(id => !groupRoleIds.has(id)).map(rid => adminApi.revokeGroupRole(assignGroupRolesTarget.id, rid)),
      ])
      setGroups(await adminApi.listGroups()); setAssignGroupRolesTarget(null)
    } catch (e) { setPageError(e instanceof Error ? e.message : 'Role assignment failed.')
    } finally { setSavingGroupRoles(false) }
  }

  // ── Manage group members ──────────────────────────────────────────────────────

  function openManageMembers(g: AdminGroup) {
    const memberSet = new Set(
      users.filter(u => u.groups.includes(g.name)).map(u => u.id)
    )
    setMemberIds(memberSet); setManageMembersGroup(g)
  }
  async function saveManageMembers() {
    if (!manageMembersGroup) return
    setSavingMembers(true)
    try {
      const currentIds = new Set(users.filter(u => u.groups.includes(manageMembersGroup.name)).map(u => u.id))
      await Promise.all([
        ...[...memberIds].filter(uid => !currentIds.has(uid)).map(uid => adminApi.addGroupMember(manageMembersGroup.id, uid)),
        ...[...currentIds].filter(uid => !memberIds.has(uid)).map(uid => adminApi.removeGroupMember(manageMembersGroup.id, uid)),
      ])
      const [refreshedUsers, refreshedGroups] = await Promise.all([adminApi.listUsers(), adminApi.listGroups()])
      setUsers(refreshedUsers); setGroups(refreshedGroups); setManageMembersGroup(null)
    } catch (e) { setPageError(e instanceof Error ? e.message : 'Member update failed.')
    } finally { setSavingMembers(false) }
  }

  // ── Render ────────────────────────────────────────────────────────────────────

  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">User Management</h1>
        <p className="page-subtitle">Manage users, groups, roles, and access control.</p>
      </div>

      {pageError && (
        <div className="mapper-error-card" style={{ marginBottom: '1rem' }}>
          <strong>Error:</strong> {pageError}
          <button className="um-dismiss" onClick={() => setPageError(null)}>✕</button>
        </div>
      )}

      {/* Tab bar */}
      <div className="um-tabs">
        {(['users', 'roles', 'groups'] as Tab[]).map(t => (
          <button key={t} className={`um-tab${tab === t ? ' um-tab--active' : ''}`} onClick={() => setTab(t)}>
            {t.charAt(0).toUpperCase() + t.slice(1)}{' '}
            <span className="um-tab-count">
              {t === 'users' ? users.length : t === 'roles' ? roles.length : groups.length}
            </span>
          </button>
        ))}
      </div>

      {loading ? <p className="mapper-loading">Loading…</p> : (
        <>
          {/* ── Users tab ───────────────────────────────────────────────────── */}
          {tab === 'users' && (
            <div>
              <div className="um-toolbar">
                <span className="um-toolbar-title">All Users</span>
                <button className="um-btn um-btn-primary" onClick={openAddUser}>+ Add User</button>
              </div>
              <div className="um-table-wrap">
                <table className="um-table">
                  <thead>
                    <tr>
                      <th className="um-th">Name</th>
                      <th className="um-th">Email</th>
                      <th className="um-th">Mobile</th>
                      <th className="um-th">Roles</th>
                      <th className="um-th">Groups</th>
                      <th className="um-th um-th-center">Active</th>
                      <th className="um-th um-th-center">API Access</th>
                      <th className="um-th um-th-center">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.length === 0
                      ? <tr><td className="um-td um-empty" colSpan={8}>No users found.</td></tr>
                      : users.map(u => (
                        <tr key={u.id} className="um-tr">
                          <td className="um-td um-td-name">
                            {u.first_name} {u.last_name}
                            {u.email_verified && <span className="um-verified" title="Email verified">✓</span>}
                          </td>
                          <td className="um-td">{u.email}</td>
                          <td className="um-td um-muted">{u.mobile_number ?? '—'}</td>
                          <td className="um-td">
                            <div className="um-badges">
                              {u.roles.length === 0 ? <span className="um-muted">—</span>
                                : u.roles.map(r => <span key={r} className="um-badge">{r}</span>)}
                            </div>
                          </td>
                          <td className="um-td">
                            <div className="um-badges">
                              {u.groups.length === 0 ? <span className="um-muted">—</span>
                                : u.groups.map(g => <span key={g} className="um-badge um-badge-group">{g}</span>)}
                            </div>
                          </td>
                          <td className="um-td um-td-center">
                            <label className="um-toggle" title={u.is_active ? 'Disable user' : 'Enable user'}>
                              <input type="checkbox" checked={u.is_active} onChange={() => void handleToggleActive(u)} />
                              <span className="um-toggle-track" />
                            </label>
                          </td>
                          <td className="um-td um-td-center">
                            <label className="um-toggle um-toggle-api" title={u.api_access ? 'Revoke API access' : 'Grant API access'}>
                              <input type="checkbox" checked={u.api_access} onChange={() => void handleToggleApi(u)} />
                              <span className="um-toggle-track" />
                            </label>
                          </td>
                          <td className="um-td um-td-center">
                            <div className="um-actions">
                              <button className="um-icon-btn" title="Edit user"           onClick={() => openEditUser(u)}>✎</button>
                              <button className="um-icon-btn" title="Assign roles"        onClick={() => openAssignRoles(u)}>◑</button>
                              <button className="um-icon-btn" title="Assign groups"       onClick={() => openAssignGroups(u)}>⊞</button>
                              <button className="um-icon-btn" title="Reset password"      onClick={() => void handleResetPassword(u)}>⟳</button>
                              <button className="um-icon-btn um-icon-btn--danger" title="Delete user" onClick={() => void deleteUser(u)}>✕</button>
                            </div>
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ── Roles tab ───────────────────────────────────────────────────── */}
          {tab === 'roles' && (
            <div>
              <div className="um-toolbar">
                <span className="um-toolbar-title">All Roles</span>
                <button className="um-btn um-btn-primary" onClick={openAddRole}>+ Add Role</button>
              </div>
              <div className="um-table-wrap">
                <table className="um-table">
                  <thead>
                    <tr>
                      <th className="um-th">Name</th>
                      <th className="um-th">Description</th>
                      <th className="um-th um-th-center">Members</th>
                      <th className="um-th um-th-center">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {roles.length === 0
                      ? <tr><td className="um-td um-empty" colSpan={4}>No roles found.</td></tr>
                      : roles.map(r => (
                        <tr key={r.id} className="um-tr">
                          <td className="um-td"><span className="um-role-name">{r.name}</span></td>
                          <td className="um-td um-muted">{r.description ?? '—'}</td>
                          <td className="um-td um-td-center"><span className="um-count">{r.user_count}</span></td>
                          <td className="um-td um-td-center">
                            <div className="um-actions">
                              <button className="um-icon-btn" title="Edit role"   onClick={() => openEditRole(r)}>✎</button>
                              <button className="um-icon-btn um-icon-btn--danger" title="Delete role" onClick={() => void deleteRole(r)}>✕</button>
                            </div>
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ── Groups tab ──────────────────────────────────────────────────── */}
          {tab === 'groups' && (
            <div>
              <div className="um-toolbar">
                <span className="um-toolbar-title">All Groups</span>
                <button className="um-btn um-btn-primary" onClick={openAddGroup}>+ Add Group</button>
              </div>
              <div className="um-table-wrap">
                <table className="um-table">
                  <thead>
                    <tr>
                      <th className="um-th">Name</th>
                      <th className="um-th">Description</th>
                      <th className="um-th">Roles</th>
                      <th className="um-th um-th-center">Members</th>
                      <th className="um-th um-th-center">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {groups.length === 0
                      ? <tr><td className="um-td um-empty" colSpan={5}>No groups found.</td></tr>
                      : groups.map(g => (
                        <tr key={g.id} className="um-tr">
                          <td className="um-td"><span className="um-role-name">{g.name}</span></td>
                          <td className="um-td um-muted">{g.description ?? '—'}</td>
                          <td className="um-td">
                            <div className="um-badges">
                              {g.roles.length === 0 ? <span className="um-muted">—</span>
                                : g.roles.map(r => <span key={r} className="um-badge">{r}</span>)}
                            </div>
                          </td>
                          <td className="um-td um-td-center"><span className="um-count">{g.member_count}</span></td>
                          <td className="um-td um-td-center">
                            <div className="um-actions">
                              <button className="um-icon-btn" title="Edit group"       onClick={() => openEditGroup(g)}>✎</button>
                              <button className="um-icon-btn" title="Assign roles"     onClick={() => openAssignGroupRoles(g)}>◑</button>
                              <button className="um-icon-btn" title="Manage members"   onClick={() => openManageMembers(g)}>⊞</button>
                              <button className="um-icon-btn um-icon-btn--danger" title="Delete group" onClick={() => void deleteGroup(g)}>✕</button>
                            </div>
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* ── Add / Edit User modal ──────────────────────────────────────────── */}
      {userModalOpen && (
        <div className="um-overlay" onClick={() => setUserModalOpen(false)}>
          <div className="um-modal" onClick={e => e.stopPropagation()}>
            <div className="um-modal-header">
              <h2 className="um-modal-title">{editingUser ? 'Edit User' : 'Add User'}</h2>
              <button className="um-modal-close" onClick={() => setUserModalOpen(false)}>✕</button>
            </div>
            <div className="um-modal-body">
              {userFormErr && <div className="auth-alert auth-alert--error">{userFormErr}</div>}
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">First Name *</label>
                  <input className="form-input" value={userForm.first_name} onChange={e => setUserForm(f => ({ ...f, first_name: e.target.value }))} />
                </div>
                <div className="form-group">
                  <label className="form-label">Last Name *</label>
                  <input className="form-input" value={userForm.last_name} onChange={e => setUserForm(f => ({ ...f, last_name: e.target.value }))} />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Email *</label>
                <input className="form-input" type="email" value={userForm.email} onChange={e => setUserForm(f => ({ ...f, email: e.target.value }))} />
              </div>
              <div className="form-group">
                <label className="form-label">Mobile Number</label>
                <input className="form-input" type="tel" placeholder="+1234567890" value={userForm.mobile_number} onChange={e => setUserForm(f => ({ ...f, mobile_number: e.target.value }))} />
              </div>
              {!editingUser && (
                <div className="form-group">
                  <label className="form-label">Password *</label>
                  <input className="form-input" type="password" autoComplete="new-password" value={userForm.password} onChange={e => setUserForm(f => ({ ...f, password: e.target.value }))} />
                </div>
              )}
            </div>
            <div className="um-modal-footer">
              <button className="um-btn um-btn-ghost" onClick={() => setUserModalOpen(false)}>Cancel</button>
              <button className="um-btn um-btn-primary" onClick={() => void saveUser()} disabled={savingUser}>{savingUser ? 'Saving…' : 'Save'}</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Add / Edit Role modal ──────────────────────────────────────────── */}
      {roleModalOpen && (
        <div className="um-overlay" onClick={() => setRoleModalOpen(false)}>
          <div className="um-modal" onClick={e => e.stopPropagation()}>
            <div className="um-modal-header">
              <h2 className="um-modal-title">{editingRole ? 'Edit Role' : 'Add Role'}</h2>
              <button className="um-modal-close" onClick={() => setRoleModalOpen(false)}>✕</button>
            </div>
            <div className="um-modal-body">
              {roleFormErr && <div className="auth-alert auth-alert--error">{roleFormErr}</div>}
              <div className="form-group">
                <label className="form-label">Name *</label>
                <input className="form-input" value={roleForm.name} onChange={e => setRoleForm(f => ({ ...f, name: e.target.value }))} />
              </div>
              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea className="form-input" rows={3} value={roleForm.description} onChange={e => setRoleForm(f => ({ ...f, description: e.target.value }))} />
              </div>
            </div>
            <div className="um-modal-footer">
              <button className="um-btn um-btn-ghost" onClick={() => setRoleModalOpen(false)}>Cancel</button>
              <button className="um-btn um-btn-primary" onClick={() => void saveRole()} disabled={savingRole}>{savingRole ? 'Saving…' : 'Save'}</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Add / Edit Group modal ─────────────────────────────────────────── */}
      {groupModalOpen && (
        <div className="um-overlay" onClick={() => setGroupModalOpen(false)}>
          <div className="um-modal" onClick={e => e.stopPropagation()}>
            <div className="um-modal-header">
              <h2 className="um-modal-title">{editingGroup ? 'Edit Group' : 'Add Group'}</h2>
              <button className="um-modal-close" onClick={() => setGroupModalOpen(false)}>✕</button>
            </div>
            <div className="um-modal-body">
              {groupFormErr && <div className="auth-alert auth-alert--error">{groupFormErr}</div>}
              <div className="form-group">
                <label className="form-label">Name *</label>
                <input className="form-input" value={groupForm.name} onChange={e => setGroupForm(f => ({ ...f, name: e.target.value }))} />
              </div>
              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea className="form-input" rows={3} value={groupForm.description} onChange={e => setGroupForm(f => ({ ...f, description: e.target.value }))} />
              </div>
            </div>
            <div className="um-modal-footer">
              <button className="um-btn um-btn-ghost" onClick={() => setGroupModalOpen(false)}>Cancel</button>
              <button className="um-btn um-btn-primary" onClick={() => void saveGroup()} disabled={savingGroup}>{savingGroup ? 'Saving…' : 'Save'}</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Assign roles to user ───────────────────────────────────────────── */}
      {assignRolesUser && (
        <div className="um-overlay" onClick={() => setAssignRolesUser(null)}>
          <div className="um-modal" onClick={e => e.stopPropagation()}>
            <div className="um-modal-header">
              <h2 className="um-modal-title">Assign Roles — {assignRolesUser.first_name} {assignRolesUser.last_name}</h2>
              <button className="um-modal-close" onClick={() => setAssignRolesUser(null)}>✕</button>
            </div>
            <div className="um-modal-body">
              {roles.length === 0
                ? <p className="um-muted">No roles defined yet. Add roles in the Roles tab first.</p>
                : <div className="um-checklist">{roles.map(r => (
                    <label key={r.id} className="um-check-item">
                      <input type="checkbox" checked={assignedRoleIds.has(r.id)} onChange={e => { const s = new Set(assignedRoleIds); e.target.checked ? s.add(r.id) : s.delete(r.id); setAssignedRoleIds(s) }} />
                      <div className="um-check-text">
                        <span className="um-check-name">{r.name}</span>
                        {r.description && <span className="um-check-desc">{r.description}</span>}
                      </div>
                    </label>
                  ))}</div>}
            </div>
            <div className="um-modal-footer">
              <button className="um-btn um-btn-ghost" onClick={() => setAssignRolesUser(null)}>Cancel</button>
              <button className="um-btn um-btn-primary" onClick={() => void saveAssignRoles()} disabled={savingAssignRoles}>{savingAssignRoles ? 'Saving…' : 'Apply'}</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Assign groups to user ──────────────────────────────────────────── */}
      {assignGroupsUser && (
        <div className="um-overlay" onClick={() => setAssignGroupsUser(null)}>
          <div className="um-modal" onClick={e => e.stopPropagation()}>
            <div className="um-modal-header">
              <h2 className="um-modal-title">Assign Groups — {assignGroupsUser.first_name} {assignGroupsUser.last_name}</h2>
              <button className="um-modal-close" onClick={() => setAssignGroupsUser(null)}>✕</button>
            </div>
            <div className="um-modal-body">
              {groups.length === 0
                ? <p className="um-muted">No groups defined yet. Add groups in the Groups tab first.</p>
                : <div className="um-checklist">{groups.map(g => (
                    <label key={g.id} className="um-check-item">
                      <input type="checkbox" checked={assignedGroupIds.has(g.id)} onChange={e => { const s = new Set(assignedGroupIds); e.target.checked ? s.add(g.id) : s.delete(g.id); setAssignedGroupIds(s) }} />
                      <div className="um-check-text">
                        <span className="um-check-name">{g.name}</span>
                        {g.description && <span className="um-check-desc">{g.description}</span>}
                      </div>
                    </label>
                  ))}</div>}
            </div>
            <div className="um-modal-footer">
              <button className="um-btn um-btn-ghost" onClick={() => setAssignGroupsUser(null)}>Cancel</button>
              <button className="um-btn um-btn-primary" onClick={() => void saveAssignGroups()} disabled={savingAssignGroups}>{savingAssignGroups ? 'Saving…' : 'Apply'}</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Assign roles to group ──────────────────────────────────────────── */}
      {assignGroupRolesTarget && (
        <div className="um-overlay" onClick={() => setAssignGroupRolesTarget(null)}>
          <div className="um-modal" onClick={e => e.stopPropagation()}>
            <div className="um-modal-header">
              <h2 className="um-modal-title">Assign Roles — {assignGroupRolesTarget.name}</h2>
              <button className="um-modal-close" onClick={() => setAssignGroupRolesTarget(null)}>✕</button>
            </div>
            <div className="um-modal-body">
              {roles.length === 0
                ? <p className="um-muted">No roles defined yet. Add roles in the Roles tab first.</p>
                : <div className="um-checklist">{roles.map(r => (
                    <label key={r.id} className="um-check-item">
                      <input type="checkbox" checked={groupRoleIds.has(r.id)} onChange={e => { const s = new Set(groupRoleIds); e.target.checked ? s.add(r.id) : s.delete(r.id); setGroupRoleIds(s) }} />
                      <div className="um-check-text">
                        <span className="um-check-name">{r.name}</span>
                        {r.description && <span className="um-check-desc">{r.description}</span>}
                      </div>
                    </label>
                  ))}</div>}
            </div>
            <div className="um-modal-footer">
              <button className="um-btn um-btn-ghost" onClick={() => setAssignGroupRolesTarget(null)}>Cancel</button>
              <button className="um-btn um-btn-primary" onClick={() => void saveAssignGroupRoles()} disabled={savingGroupRoles}>{savingGroupRoles ? 'Saving…' : 'Apply'}</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Manage group members ───────────────────────────────────────────── */}
      {manageMembersGroup && (
        <div className="um-overlay" onClick={() => setManageMembersGroup(null)}>
          <div className="um-modal" onClick={e => e.stopPropagation()}>
            <div className="um-modal-header">
              <h2 className="um-modal-title">Members — {manageMembersGroup.name}</h2>
              <button className="um-modal-close" onClick={() => setManageMembersGroup(null)}>✕</button>
            </div>
            <div className="um-modal-body">
              {users.length === 0
                ? <p className="um-muted">No users in the system yet.</p>
                : <div className="um-checklist">{users.map(u => (
                    <label key={u.id} className="um-check-item">
                      <input type="checkbox" checked={memberIds.has(u.id)} onChange={e => { const s = new Set(memberIds); e.target.checked ? s.add(u.id) : s.delete(u.id); setMemberIds(s) }} />
                      <div className="um-check-text">
                        <span className="um-check-name">{u.first_name} {u.last_name}</span>
                        <span className="um-check-desc">{u.email}</span>
                      </div>
                    </label>
                  ))}</div>}
            </div>
            <div className="um-modal-footer">
              <button className="um-btn um-btn-ghost" onClick={() => setManageMembersGroup(null)}>Cancel</button>
              <button className="um-btn um-btn-primary" onClick={() => void saveManageMembers()} disabled={savingMembers}>{savingMembers ? 'Saving…' : 'Apply'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
