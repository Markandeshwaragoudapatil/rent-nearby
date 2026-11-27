import { useEffect, useState } from "react"
import { Link, Navigate } from "react-router-dom"
import { ArrowRight, ShieldCheck } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import { apiRequest } from "../services/api"

const emptyForm = { business_name: "", description: "", contact_phone: "", city: "Bengaluru" }

export default function OwnerApplicationPage() {
  const { user, refreshUser } = useAuth()
  const [application, setApplication] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    let active = true
    apiRequest("/owner/application")
      .then(result => {
        if (!active) return
        const current = result.application
        setApplication(current)
        if (current) setForm({
          business_name: current.business_name || "",
          description: current.description || "",
          contact_phone: current.contact_phone || "",
          city: current.city || "Bengaluru",
        })
      })
      .catch(requestError => { if (active) setError(requestError.message || "Could not load your application.") })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [])

  if (user?.role === "OWNER") return <Navigate to="/owner" replace />
  if (user?.role === "ADMIN") return <Navigate to="/admin" replace />

  function updateField(event) {
    setForm(current => ({ ...current, [event.target.name]: event.target.value }))
  }

  async function submit(event) {
    event.preventDefault()
    setSubmitting(true)
    setError("")
    try {
      const result = await apiRequest("/owner/application", { method: "POST", body: form })
      setApplication(result.application)
      await refreshUser()
    } catch (requestError) {
      setError(requestError.message || "Your application could not be submitted.")
    } finally {
      setSubmitting(false)
    }
  }

  const locked = application?.status === "PENDING" || application?.status === "APPROVED"

  return (
    <main className="basic-page page-shell">
      <span className="eyebrow">BECOME A RENTNEARBY OWNER</span>
      <h1>Turn useful things into <em>extra value.</em></h1>
      <p className="basic-lede">Tell us what you plan to rent out. An administrator reviews each application before owner tools are enabled.</p>
      {loading ? <p role="status">Loading your application…</p> : <>
        {application?.status === "PENDING" && <div className="workflow-status"><ShieldCheck size={18}/><div><b>Application under review</b><p>Your account remains a renter until an administrator approves the application.</p></div></div>}
        {application?.status === "APPROVED" && <div className="workflow-status"><ShieldCheck size={18}/><div><b>Owner access approved</b><p>Your owner access is active. <Link to="/owner">Open your owner workspace</Link>.</p></div></div>}
        {application?.status === "REJECTED" && <div className="workflow-status workflow-rejected"><div><b>Changes requested</b><p>{application.decision_note || "Please update the details and submit again."}</p></div></div>}
        {!locked && <section className="workflow-card">
          <h2>{application?.status === "REJECTED" ? "Update your application" : "Tell us about your rental activity"}</h2>
          <form className="auth-form" onSubmit={submit}>
            <label>Business or display name<input name="business_name" value={form.business_name} onChange={updateField} maxLength={120} required/></label>
            <label>What do you plan to rent out?<textarea name="description" value={form.description} onChange={updateField} minLength={30} maxLength={1500} rows={5} required placeholder="Mention the kinds of items and the neighbourhoods you can serve."/></label>
            <label>Contact phone<input name="contact_phone" type="tel" value={form.contact_phone} onChange={updateField} maxLength={20} required placeholder="+91 9876543210"/></label>
            <label>City<input name="city" value={form.city} onChange={updateField} maxLength={100} required/></label>
            {error && <p className="form-message form-error" role="alert">{error}</p>}
            <button className="button button-dark auth-submit" type="submit" disabled={submitting}>{submitting ? "Submitting…" : "Submit for review"} <ArrowRight size={17}/></button>
          </form>
        </section>}
      </>}
      <p className="workflow-footnote">We do not ask for Aadhaar or identity-document uploads in this application.</p>
    </main>
  )
}
