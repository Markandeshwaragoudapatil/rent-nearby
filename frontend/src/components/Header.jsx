import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { Menu, X, ArrowUpRight } from 'lucide-react'

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false)
  const closeMenu = () => setMenuOpen(false)
  return (
    <header className="site-header">
      <div className="nav-wrap page-shell">
        <Link to="/" className="brand" aria-label="RentNearby home" onClick={closeMenu}>
          <span className="brand-mark">r<span>.</span></span>
          <span>rentnearby</span>
        </Link>
        <button className="mobile-menu-button" onClick={() => setMenuOpen(!menuOpen)} aria-label={menuOpen ? 'Close navigation' : 'Open navigation'} aria-expanded={menuOpen}>
          {menuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
        <nav className={`main-nav ${menuOpen ? 'is-open' : ''}`} aria-label="Main navigation">
          <NavLink to="/browse" onClick={closeMenu}>Explore</NavLink>
          <a href="#categories" onClick={closeMenu}>Categories</a>
          <a href="#how-it-works" onClick={closeMenu}>How it works</a>
          <Link to="/list-item" className="nav-owner" onClick={closeMenu}>List your item <ArrowUpRight size={15} /></Link>
          <Link to="/login" className="nav-login" onClick={closeMenu}>Log in</Link>
          <Link to="/register" className="button button-dark nav-cta" onClick={closeMenu}>Get started</Link>
        </nav>
      </div>
    </header>
  )
}
