import { MapPin, ArrowUpRight, Camera } from "lucide-react"
import { Link } from "react-router-dom"

function formatPrice(product) {
  if (Number.isInteger(product.pricePaise)) {
    return (product.pricePaise / 100).toLocaleString("en-IN", { maximumFractionDigits: 2 })
  }
  return Number(product.price || 0).toLocaleString("en-IN")
}

export default function ProductCard({ product }) {
  return (
    <article className="product-card">
      <Link to={`/product/${product.id}`} className="product-image-wrap" aria-label={`View ${product.name}`}>
        {product.image
          ? <img src={product.image} alt={product.name} loading="lazy"/>
          : <span className="product-placeholder" aria-hidden="true"><Camera size={34}/></span>}
        <span className="product-tag">{product.tag || (product.isLive ? "Live listing" : "Sample item")}</span>
        <span className="image-arrow"><ArrowUpRight size={17}/></span>
      </Link>
      <div className="product-info">
        <div className="product-meta"><span>{product.category}</span><span className={product.isLive ? "live-label" : "demo-label"}>{product.isLive ? "Live" : "Demo item"}</span></div>
        <h3><Link to={`/product/${product.id}`}>{product.name}</Link></h3>
        <p className="product-location"><MapPin size={14}/> {product.location}, Bengaluru</p>
        <div className="product-bottom"><p><strong>₹{formatPrice(product)}</strong><span> / {product.unit}</span></p><Link to={`/product/${product.id}`} className="text-link">View item</Link></div>
      </div>
    </article>
  )
}
