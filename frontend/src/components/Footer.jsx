import { Link } from 'react-router-dom'
import { ArrowUpRight, Instagram, Linkedin } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="page-shell footer-top">
        <div className="footer-brand"><Link to="/" className="brand"><span className="brand-mark">r<span>.</span></span><span>rentnearby</span></Link><p>Good things are better shared.<br />Find what you need, close to home.</p></div>
        <div className="footer-links"><div><b>Explore</b><Link to="/browse">Browse items</Link><a href="/#categories">Categories</a><a href="/#how-it-works">How it works</a></div><div><b>Community</b><Link to="/list-item">List an item</Link><Link to="/about">Our story</Link><Link to="/contact">Contact</Link></div><div><b>Information</b><Link to="/terms">Terms of use</Link><Link to="/privacy">Privacy policy</Link><Link to="/safety">Trust & safety</Link></div></div>
      </div>
      <div className="page-shell footer-bottom"><span>© 2026 RentNearby. Built for sharing.</span><span className="footer-social"><a href="https://www.instagram.com/" aria-label="Instagram"><Instagram size={17}/></a><a href="https://www.linkedin.com/" aria-label="LinkedIn"><Linkedin size={17}/></a><span>Made for Bengaluru <ArrowUpRight size={14}/></span></span></div>
    </footer>
  )
}
