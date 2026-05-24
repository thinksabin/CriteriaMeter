import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../api/authApi'
import { settingsApi, type AuthSettings } from '../api/settingsApi'
import { useAuth } from '../context/AuthContext'

// ── Password visibility toggle ────────────────────────────────────────────────

function PasswordInput({
  id,
  value,
  onChange,
  autoComplete,
  disabled,
}: {
  id: string
  value: string
  onChange: (v: string) => void
  autoComplete: string
  disabled: boolean
}) {
  const [visible, setVisible] = useState(false)
  return (
    <div className="pw-input-wrap">
      <input
        id={id}
        type={visible ? 'text' : 'password'}
        className="form-input pw-input"
        value={value}
        onChange={e => onChange(e.target.value)}
        autoComplete={autoComplete}
        required
        disabled={disabled}
      />
      <button
        type="button"
        className="pw-toggle-btn"
        onClick={() => setVisible(v => !v)}
        aria-label={visible ? 'Hide password' : 'Show password'}
        tabIndex={-1}
        disabled={disabled}
      >
        {visible ? '🙈' : '👁'}
      </button>
    </div>
  )
}

// ── Password strength ─────────────────────────────────────────────────────────

type StrengthLevel = 'weak' | 'medium' | 'strong'

function calcStrength(pw: string): { level: StrengthLevel; label: string } {
  if (!pw) return { level: 'weak', label: '' }
  let score = 0
  if (pw.length >= 8)  score++
  if (pw.length >= 12) score++
  if (pw.length >= 16) score++
  if (/[A-Z]/.test(pw)) score++
  if (/[a-z]/.test(pw)) score++
  if (/[0-9]/.test(pw)) score++
  if (/[^A-Za-z0-9]/.test(pw)) score++
  const level: StrengthLevel = score <= 2 ? 'weak' : score <= 4 ? 'medium' : 'strong'
  return { level, label: score <= 2 ? 'Weak' : score <= 4 ? 'Medium' : 'Strong' }
}

function StrengthMeter({ password }: { password: string }) {
  const { level, label } = calcStrength(password)
  if (!password) return null
  return (
    <div className="pw-strength">
      <div className="pw-strength-bars">
        <span className={`pw-bar pw-bar--${level}`} />
        <span className={`pw-bar ${level === 'medium' || level === 'strong' ? `pw-bar--${level}` : 'pw-bar--empty'}`} />
        <span className={`pw-bar ${level === 'strong' ? 'pw-bar--strong' : 'pw-bar--empty'}`} />
      </div>
      <span className={`pw-strength-label pw-strength-label--${level}`}>{label}</span>
    </div>
  )
}

function requirementsText(s: AuthSettings): string {
  const parts: string[] = [`at least ${s.min_password_length} characters`]
  if (s.require_uppercase)    parts.push('one uppercase letter')
  if (s.require_number)       parts.push('one number')
  if (s.require_special_char) parts.push('one special character')
  return parts.join(', ')
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Settings() {
  const { logout } = useAuth()
  const navigate   = useNavigate()

  const [settings,   setSettings]   = useState<AuthSettings | null>(null)
  const [currentPw,  setCurrentPw]  = useState('')
  const [newPw,      setNewPw]      = useState('')
  const [confirmPw,  setConfirmPw]  = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error,      setError]      = useState<string | null>(null)
  const [success,    setSuccess]    = useState(false)

  useEffect(() => {
    settingsApi.getAuthSettings().then(setSettings).catch(() => null)
  }, [])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setSuccess(false)

    if (newPw !== confirmPw) {
      setError('New passwords do not match.')
      return
    }

    setSubmitting(true)
    try {
      await authApi.changePassword({
        current_password: currentPw,
        new_password:     newPw,
        confirm_password: confirmPw,
      })
      setSuccess(true)
      setTimeout(() => { logout(); navigate('/login') }, 2000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Password change failed.')
    } finally {
      setSubmitting(false)
    }
  }

  const disabled = submitting || success

  return (
    <div className="settings-page">
      <h1 className="page-title">Settings</h1>

      <div className="settings-card">
        <h2 className="settings-card-title">Change Password</h2>
        <p className="settings-card-subtitle">
          You will be signed out after a successful password change.
        </p>

        {settings && (
          <p className="settings-requirements">
            Password must contain {requirementsText(settings)}.
          </p>
        )}

        {error   && <div className="auth-alert">{error}</div>}
        {success && <div className="auth-alert auth-alert--success">Password changed. Redirecting to login…</div>}

        <form onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label className="form-label" htmlFor="current-pw">Current password</label>
            <PasswordInput
              id="current-pw"
              value={currentPw}
              onChange={setCurrentPw}
              autoComplete="current-password"
              disabled={disabled}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="new-pw">New password</label>
            <PasswordInput
              id="new-pw"
              value={newPw}
              onChange={setNewPw}
              autoComplete="new-password"
              disabled={disabled}
            />
            <StrengthMeter password={newPw} />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="confirm-pw">Confirm new password</label>
            <PasswordInput
              id="confirm-pw"
              value={confirmPw}
              onChange={setConfirmPw}
              autoComplete="new-password"
              disabled={disabled}
            />
          </div>

          <button
            type="submit"
            className="form-submit"
            disabled={disabled || !currentPw || !newPw || !confirmPw}
          >
            {submitting ? 'Saving…' : 'Change password'}
          </button>
        </form>
      </div>
    </div>
  )
}
