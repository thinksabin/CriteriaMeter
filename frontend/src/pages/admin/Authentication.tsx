import { useEffect, useState } from 'react'
import { AuthSettings, settingsApi } from '../../api/settingsApi'

// ── Toggle row ─────────────────────────────────────────────────────────────────

function SettingToggle({
  label, description, checked, onChange,
}: {
  label: string; description: string; checked: boolean; onChange: (v: boolean) => void
}) {
  return (
    <div className="as-row">
      <div className="as-row-text">
        <span className="as-row-label">{label}</span>
        <span className="as-row-desc">{description}</span>
      </div>
      <label className="um-toggle">
        <input type="checkbox" checked={checked} onChange={e => onChange(e.target.checked)} />
        <span className="um-toggle-track" />
      </label>
    </div>
  )
}

// ── Page ───────────────────────────────────────────────────────────────────────

export default function Authentication() {
  const [settings, setSettings] = useState<AuthSettings | null>(null)
  const [loading,  setLoading]  = useState(true)
  const [saving,   setSaving]   = useState(false)
  const [loadErr,  setLoadErr]  = useState<string | null>(null)
  const [saveMsg,  setSaveMsg]  = useState<{ ok: boolean; text: string } | null>(null)

  useEffect(() => {
    settingsApi.getAuthSettings()
      .then(s  => { setSettings(s); setLoading(false) })
      .catch(e => { setLoadErr(e instanceof Error ? e.message : 'Failed to load settings.'); setLoading(false) })
  }, [])

  function patch<K extends keyof AuthSettings>(key: K, value: AuthSettings[K]) {
    if (!settings) return
    setSettings({ ...settings, [key]: value })
    setSaveMsg(null)
  }

  async function save() {
    if (!settings) return
    setSaving(true)
    setSaveMsg(null)
    try {
      const updated = await settingsApi.updateAuthSettings(settings)
      setSettings(updated)
      setSaveMsg({ ok: true, text: 'Settings saved successfully.' })
    } catch (e) {
      setSaveMsg({ ok: false, text: e instanceof Error ? e.message : 'Save failed.' })
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="page-content"><p className="mapper-loading">Loading…</p></div>

  if (loadErr) return (
    <div className="page-content">
      <div className="mapper-error-card"><strong>Error:</strong> {loadErr}</div>
    </div>
  )

  if (!settings) return null

  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">Authentication</h1>
        <p className="page-subtitle">Configure registration and password security policies.</p>
      </div>

      {/* ── User Registration ───────────────────────────────────────────────── */}
      <section className="as-section">
        <h2 className="as-section-title">User Registration</h2>

        <SettingToggle
          label="Enable sign-up"
          description="Allow new users to register via the sign-up page. Disable to restrict account creation to administrators only."
          checked={settings.signup_enabled}
          onChange={v => patch('signup_enabled', v)}
        />
      </section>

      {/* ── Password Policy ─────────────────────────────────────────────────── */}
      <section className="as-section">
        <h2 className="as-section-title">Password Policy</h2>

        {/* Minimum length */}
        <div className="as-row">
          <div className="as-row-text">
            <span className="as-row-label">Minimum password length</span>
            <span className="as-row-desc">Passwords shorter than this value will be rejected. Range: 6–128.</span>
          </div>
          <input
            className="as-number-input"
            type="number"
            min={6}
            max={128}
            value={settings.min_password_length}
            onChange={e => {
              const n = Math.max(6, Math.min(128, Number(e.target.value)))
              patch('min_password_length', n)
            }}
          />
        </div>

        <SettingToggle
          label="Require a number"
          description="Password must contain at least one numeric digit (0–9)."
          checked={settings.require_number}
          onChange={v => patch('require_number', v)}
        />

        <SettingToggle
          label="Require an uppercase letter"
          description="Password must contain at least one uppercase character (A–Z)."
          checked={settings.require_uppercase}
          onChange={v => patch('require_uppercase', v)}
        />

        <SettingToggle
          label="Require a special character"
          description="Password must contain at least one special character (e.g. ! @ # $ % ^)."
          checked={settings.require_special_char}
          onChange={v => patch('require_special_char', v)}
        />
      </section>

      {/* ── Footer ─────────────────────────────────────────────────────────── */}
      <div className="as-footer">
        {saveMsg && (
          <span className={`as-save-msg${saveMsg.ok ? ' as-save-msg--ok' : ' as-save-msg--err'}`}>
            {saveMsg.text}
          </span>
        )}
        <button className="um-btn um-btn-primary" onClick={() => void save()} disabled={saving}>
          {saving ? 'Saving…' : 'Save Changes'}
        </button>
      </div>
    </div>
  )
}
