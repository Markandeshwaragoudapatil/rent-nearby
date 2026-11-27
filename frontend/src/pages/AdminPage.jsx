import { useCallback, useEffect, useState } from "react"
import { Check, RefreshCw, ShieldCheck, X } from "lucide-react"
import { apiRequest } from "../services/api"

export default function AdminPage() {
  const [applications, setApplications] = useState([])
  const [products, setProducts] = useState([])
  const [notes, setNotes] = useState({})
  const [loading, setLoading] = useState(true)
  const [working, setWorking] = useState("")
  const [error, setError] = useState("")
  const [notice, setNotice] = useState("")

  const loadQueues = useCallback(async () => {
    setLoading(true)
    setError("")
    try {
      const [ownerResult, productResult] = await Promise.all([
        apiRequest("/admin/owner-applications?status=PENDING"),
        apiRequest("/admin/products/pending"),
      ])
      setApplications(ownerResult.items || [])
      setProducts(productResult.items || [])
    } catch (requestError) {
      setError(requestError.message || "Could not load the moderation queue.")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadQueues() }, [loadQueues])

  async function decide(type, id, decision) {
    const note = notes[id] || ""
    if (decision === "REJECT" && !note.trim()) {
      setError("Add a short reason before rejecting an application or listing.")
      return
    }
    const key = type + ":" + id
    setWorking(key)
    setError("")
    setNotice("")
    try {
      const path = type === "owner"
        ? "/admin/owner-applications/" + id + "/decision"
        : "/admin/products/" + id + "/decision"
      await apiRequest(path, { method: "PATCH", body: { decision, note } })
      setNotice((type === "owner" ? "Owner application" : "Listing") + " " + decision.toLowerCase() + "d.")
      await loadQueues()
    } catch (requestError) {
      setError(requestError.message || "The moderation action failed.")
    } finally {
      setWorking("")
    }
  }

  return (
    <main className="basic-page page-shell admin-page">
      <span className="eyebrow">RENTNEARBY OPERATIONS</span>
      <h1>Trust & <em>moderation.</em></h1>
      <p className="basic-lede">Review owner applications and submitted listings before they become active on the marketplace.</p>
      <div className="admin-toolbar">
        <span><ShieldCheck size={16}/> Admin-only workspace</span>
        <button className="button button-outline" type="button" onClick={loadQueues} disabled={loading}><RefreshCw size={15}/> Refresh</button>
      </div>
      {error && <p className="form-message form-error" role="alert">{error}</p>}
      {notice && <p className="workflow-status" role="status">{notice}</p>}
      {loading ? <p role="status">Loading moderation queue…</p> : <>
        <section className="admin-section">
          <div className="admin-section-heading"><h2>Owner applications</h2><span>{applications.length} pending</span></div>
          {applications.length === 0 ? <p className="admin-empty">No owner applications waiting for review.</p> : applications.map(item => (
            <article className="admin-card" key={item.id}>
              <div className="admin-card-heading"><div><span className="eyebrow">OWNER APPLICATION</span><h3>{item.business_name}</h3></div><span className="status-pill">{item.status}</span></div>
              <p>{item.description}</p>
              <div className="admin-meta"><span>{item.city}</span><span>{item.contact_phone}</span><span>User {item.user_id}</span></div>
              <label className="admin-note">Decision note<input value={notes[item.id] || ""} onChange={event => setNotes(current => ({ ...current, [item.id]: event.target.value }))} placeholder="Required when rejecting" maxLength={500}/></label>
              <div className="admin-actions">
                <button className="button button-dark" onClick={() => decide("owner", item.id, "APPROVE")} disabled={working === "owner:" + item.id}><Check size={15}/> Approve owner</button>
                <button className="button button-outline" onClick={() => decide("owner", item.id, "REJECT")} disabled={working === "owner:" + item.id}><X size={15}/> Reject</button>
              </div>
            </article>
          ))}
        </section>
        <section className="admin-section">
          <div className="admin-section-heading"><h2>Listings awaiting review</h2><span>{products.length} pending</span></div>
          {products.length === 0 ? <p className="admin-empty">No submitted listings waiting for review.</p> : products.map(item => (
            <article className="admin-card" key={item.id}>
              <div className="admin-card-heading"><div><span className="eyebrow">LISTING REVIEW</span><h3>{item.title}</h3></div><span className="status-pill">PENDING</span></div>
              <p>{item.description}</p>
              <div className="admin-meta"><span>{item.category?.name}</span><span>{item.condition?.replaceAll("_", " ")}</span><span>{item.locality}</span></div>
              <label className="admin-note">Decision note<input value={notes[item.id] || ""} onChange={event => setNotes(current => ({ ...current, [item.id]: event.target.value }))} placeholder="Required when rejecting" maxLength={500}/></label>
              <div className="admin-actions">
                <button className="button button-dark" onClick={() => decide("product", item.id, "APPROVE")} disabled={working === "product:" + item.id}><Check size={15}/> Approve listing</button>
                <button className="button button-outline" onClick={() => decide("product", item.id, "REJECT")} disabled={working === "product:" + item.id}><X size={15}/> Reject</button>
              </div>
            </article>
          ))}
        </section>
      </>}
    </main>
  )
}
