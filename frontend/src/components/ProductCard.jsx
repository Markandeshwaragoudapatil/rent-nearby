import { MapPin, ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function ProductCard({ product }) {
  return (
    <article className="product-card">
      <Link to={`/product/${product.id}`} className="product-image-wrap" aria-label={`View ${product.name}`}>
        <img src={product.image} alt={product.name} loading="lazy" />
        <span className="product-tag">{product.tag}</span>
        <span className="image-arrow"><ArrowUpRight size={17} /></span>
      </Link>
      <div className="product-info">
        <div className="product-meta"><span>{product.category}</span><span className="demo-label">Demo item</span></div>
        <h3><Link to={`/product/${product.id}`}>{product.name}</Link></h3>
        <p className="product-location"><MapPin size={14} /> {product.location}, Bengaluru</p>
        <div className="product-bottom"><p><strong>₹{product.price.toLocaleString('en-IN')}</strong><span> / {product.unit}</span></p><Link to={`/product/${product.id}`} className="text-link">View item</Link></div>
      </div>
    </article>
  )
}
