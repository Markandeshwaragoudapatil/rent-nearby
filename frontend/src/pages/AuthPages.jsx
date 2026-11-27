import { useState } from "react"
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom"
import { ArrowRight, ShieldCheck } from "lucide-react"
import { useAuth } from "../context/AuthContext"

function AuthShell({ eyebrow, title, description, children, footer }) {
  return (
    <main className="auth-page page-shell">
      <section className="auth-card">
        <span className="eyebrow">{eyebrow}</span>
        <h1>{title}</h1>
        <p className="auth-description">{description}</p>
        {children}
        <div className="auth-trust"><ShieldCheck size={16}/> Your password is protected by the RentNearby API.</div>
        {footer}
      </section>
    </main>
  )
}

export function LoginPage() {
  const { user, login, connectionError } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [submitting, setSubmitting] = useState(false)

  if (user) return <Navigate to={user.role === "OWNER" ? "/owner" : "/account"} replace />

  async function handleSubmit(event) {
    event.preventDefault()
    setError("")
    setSubmitting(true)
    try {
      const signedIn = await login({ email: email.trim(), password })
      const fallback = signedIn.role === "OWNER" ? "/owner" : "/account"
      navigate(location.state?.from?.pathname || fallback, { replace: true })
    } catch (requestError) {
      setError(requestError.message || "Unable to sign in. Please try again.")
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthShell eyebrow="WELCOME BACK" title="Good to see you." description="Sign in to manage your rentals and requests."
      footer={<p className="auth-switch">New to RentNearby? <Link to="/register">Create an account</Link></p>}>
      {connectionError && <p className="form-message form-error" role="alert">{connectionError}</p>}
      <form className="auth-form" onSubmit={handleSubmit}>
        <label>Email address<input type="email" autoComplete="email" value={email} onChange={event => setEmail(event.target.value)} required maxLength={255}/></label>
        <label>Password<input type="password" autoComplete="current-password" value={password} onChange={event => setPassword(event.target.value)} required/></label>
        {error && <p className="form-message form-error" role="alert">{error}</p>}
        <button className="button button-dark auth-submit" type="submit" disabled={submitting}>
          {submitting ? "Signing in…" : "Sign in"} <ArrowRight size={17}/>
        </button>
      </form>
    </AuthShell>
  )
}

export function RegisterPage() {
  const { user, register, connectionError } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [error, setError] = useState("")
  const [submitting, setSubmitting] = useState(false)

  if (user) return <Navigate to="/account" replace />

  async function handleSubmit(event) {
    event.preventDefault()
    setError("")
    if (password !== confirmPassword) {
      setError("The passwords do not match.")
      return
    }
    setSubmitting(true)
    try {
      await register({ name: name.trim(), email: email.trim(), password })
      navigate("/account", { replace: true })
    } catch (requestError) {
      setError(requestError.message || "Unable to create your account. Please try again.")
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthShell eyebrow="JOIN YOUR NEIGHBOURHOOD" title="Make yourself at home." description="Create a renter account to save items and send booking requests."
      footer={<p className="auth-switch">Already have an account? <Link to="/login">Sign in</Link></p>}>
      {connectionError && <p className="form-message form-error" role="alert">{connectionError}</p>}
      <form className="auth-form" onSubmit={handleSubmit}>
        <label>Your name<input type="text" autoComplete="name" value={name} onChange={event => setName(event.target.value)} required maxLength={100}/></label>
        <label>Email address<input type="email" autoComplete="email" value={email} onChange={event => setEmail(event.target.value)} required maxLength={255}/></label>
        <label>Password<input type="password" autoComplete="new-password" value={password} onChange={event => setPassword(event.target.value)} required minLength={12} maxLength={128}/><small>Use at least 12 characters.</small></label>
        <label>Confirm password<input type="password" autoComplete="new-password" value={confirmPassword} onChange={event => setConfirmPassword(event.target.value)} required minLength={12} maxLength={128}/></label>
        {error && <p className="form-message form-error" role="alert">{error}</p>}
        <button className="button button-dark auth-submit" type="submit" disabled={submitting}>
          {submitting ? "Creating account…" : "Create renter account"} <ArrowRight size={17}/>
        </button>
        <p className="auth-legal">By creating an account, you agree to review our <Link to="/terms">terms</Link> and <Link to="/privacy">privacy notice</Link>.</p>
      </form>
    </AuthShell>
  )
}

export function AccountPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState("")
  const [submitting, setSubmitting] = useState(false)

  async function handleLogout() {
    setSubmitting(true)
    setError("")
    try {
      await logout()
      navigate("/", { replace: true })
    } catch (requestError) {
      setError(requestError.message || "Could not sign out.")
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="basic-page page-shell account-page">
      <span className="eyebrow">YOUR RENTNEARBY ACCOUNT</span>
      <h1>Welcome, <em>{user?.name?.split(" ")[0] || "neighbour"}.</em></h1>
      <p className="basic-lede">Your account is connected to the RentNearby API.</p>
      <div className="account-summary">
        <span className="account-avatar">{user?.name?.charAt(0)?.toUpperCase() || "R"}</span>
        <div><b>{user?.name}</b><small>{user?.email}</small><small>Account type: {user?.role}</small></div>
      </div>
      {error && <p className="form-message form-error" role="alert">{error}</p>}
      <button className="button button-outline" onClick={handleLogout} disabled={submitting}>{submitting ? "Signing out…" : "Sign out"}</button>
    </main>
  )
}

export function OwnerPage() {
  const { user } = useAuth()
  return (
    <main className="basic-page page-shell">
      <span className="eyebrow">OWNER WORKSPACE</span>
      <h1>Good to have you, <em>{user?.name?.split(" ")[0]}.</em></h1>
      <p className="basic-lede">Your owner account is authenticated. Listing management and booking requests will be connected in the next frontend milestone.</p>
      <div className="demo-notice"><ShieldCheck size={15}/> Owner access is restricted by the backend role.</div>
    </main>
  )
}
