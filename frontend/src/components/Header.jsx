import { useState } from "react"
import { Link, NavLink, useNavigate } from "react-router-dom"
import { Menu, X, ArrowUpRight } from "lucide-react"
import { useAuth } from "../context/AuthContext"

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false)
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const closeMenu = () => setMenuOpen(false)

  async function handleLogout() {
    closeMenu()
    try {
      await logout()
      navigate("/", { replace: true })
    } catch {
      navigate("/account", { replace: true })
    }
  }

  return (
    <header className="site-header">
      <div className="nav-wrap page-shell">
        <Link to="/" className="brand" aria-label="RentNearby home" onClick={closeMenu}>
          <span className="brand-mark">r<span>.</span></span>
          <span>rentnearby</span>
        </Link>
        <button className="mobile-menu-button" onClick={() => setMenuOpen(!menuOpen)} aria-label={menuOpen ? "Close navigation" : "Open navigation"} aria-expanded={menuOpen}>
          {menuOpen ? <X size={22}/> : <Menu size={22}/>}
        </button>
        <nav className={`main-nav ${menuOpen ? "is-open" : ""}`} aria-label="Main navigation">
          <NavLink to="/browse" onClick={closeMenu}>Explore</NavLink>
          <a href="/#categories" onClick={closeMenu}>Categories</a>
          <a href="/#how-it-works" onClick={closeMenu}>How it works</a>
          <Link to="/list-item" className="nav-owner" onClick={closeMenu}>List your item <ArrowUpRight size={15}/></Link>
          {user ? <>
            {user.role === "OWNER" && <Link to="/owner" className="nav-login" onClick={closeMenu}>Owner workspace</Link>}
            {user.role === "ADMIN" && <Link to="/admin" className="nav-login" onClick={closeMenu}>Admin workspace</Link>}
            <Link to="/account" className="nav-login" onClick={closeMenu}>My account</Link>
            <button type="button" className="nav-logout" onClick={handleLogout}>Log out</button>
          </> : <>
            <Link to="/login" className="nav-login" onClick={closeMenu}>Log in</Link>
            <Link to="/register" className="button button-dark nav-cta" onClick={closeMenu}>Get started</Link>
          </>}
        </nav>
      </div>
    </header>
  )
}
