import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authApi } from '../api/authApi'

export default function SignUp() {
  const navigate = useNavigate()

  const [firstName, setFirstName]             = useState('')
  const [lastName,  setLastName]              = useState('')
  const [email,     setEmail]                 = useState('')
  const [password,  setPassword]              = useState('')
  const [confirm,   setConfirm]               = useState('')
  const [error,     setError]                 = useState<string | null>(null)
  const [loading,   setLoading]               = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)

    if (password !== confirm) {
      setError('Passwords do not match.')
      return
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }

    setLoading(true)
    try {
      await authApi.signup({
        first_name: firstName.trim(),
        last_name:  lastName.trim(),
        email:      email.trim(),
        password,
      })
      navigate('/login', { state: { registered: true } })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign up failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-logo">
        <span>⬡</span>
        <span>CriteriaMeter</span>
      </div>

      <div className="auth-card">
        <h1 className="auth-card-title">Create an account</h1>
        <p className="auth-card-subtitle">Get started with CriteriaMeter.</p>

        {error && <div className="auth-alert">{error}</div>}

        <form onSubmit={handleSubmit} noValidate>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="firstName">First name</label>
              <input
                id="firstName"
                type="text"
                className="form-input"
                placeholder="Jane"
                value={firstName}
                onChange={e => setFirstName(e.target.value)}
                required
                autoComplete="given-name"
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="lastName">Last name</label>
              <input
                id="lastName"
                type="text"
                className="form-input"
                placeholder="Doe"
                value={lastName}
                onChange={e => setLastName(e.target.value)}
                required
                autoComplete="family-name"
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              className="form-input"
              placeholder="you@example.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className="form-input"
              placeholder="Min. 8 characters"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="confirm">Confirm password</label>
            <input
              id="confirm"
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={confirm}
              onChange={e => setConfirm(e.target.value)}
              required
              autoComplete="new-password"
            />
          </div>

          <button type="submit" className="form-submit" disabled={loading}>
            {loading ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account?{' '}
          <Link to="/login">Log in</Link>
        </p>
      </div>
    </div>
  )
}
