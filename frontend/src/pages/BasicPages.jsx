import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, ArrowUpRight, Camera, Search } from 'lucide-react'
import { demoProducts } from '../data/marketplace'
import ProductCard from '../components/ProductCard'

export function Browse() {
  const params = new URLSearchParams(window.location.search)
  const query = (params.get('q') || '').toLowerCase()
  const category = params.get('category') || ''
  const filtered = demoProducts.filter(p => (!query || `${p.name} ${p.category} ${p.location}`.toLowerCase().includes(query)) && (!category || p.category.toLowerCase().includes(category.toLowerCase()) || category.toLowerCase().includes(p.category.toLowerCase())))
  return <main className="basic-page page-shell"><span className="eyebrow">THE LOCAL FINDS</span><h1>Explore what's <em>around.</em></h1><p className="basic-lede">Discover the kind of useful things your neighbours could share. This preview catalogue is not live inventory.</p><div className="demo-notice"><Search size={15}/> Preview catalogue · Sample listings only</div>{filtered.length ? <div className="product-grid browse-grid">{filtered.map(p => <ProductCard product={p} key={p.id}/>)}</div> : <div className="empty-state"><Camera size={30}/><h2>No sample items found</h2><p>Try another search or explore all categories.</p><Link to="/browse" className="button button-dark">Clear search</Link></div>}</main>
}

export function ProductDetail() {
  const { id } = useParams(); const product = demoProducts.find(p => p.id === id)
  if (!product) return <main className="basic-page page-shell"><h1>Item not found</h1><p>This item may have moved or is not part of the preview catalogue.</p><Link to="/browse" className="text-link"><ArrowLeft size={16}/> Back to explore</Link></main>
  return <main className="basic-page page-shell detail-page"><Link to="/browse" className="text-link"><ArrowLeft size={16}/> Back to explore</Link><div className="detail-layout"><img src={product.image} alt={product.name}/><div><span className="demo-label">DEMO ITEM · NOT BOOKABLE</span><span className="eyebrow">{product.category}</span><h1>{product.name}</h1><p className="product-location">{product.location}, Bengaluru</p><p>{product.description}</p><h2>₹{product.price.toLocaleString('en-IN')} <small>/ {product.unit}</small></h2><p className="detail-disclaimer">This is illustrative content. Live availability, owner details and booking are not connected yet.</p><Link to="/browse" className="button button-dark">Continue exploring <ArrowUpRight size={17}/></Link></div></div></main>
}

export function InfoPage({ title, text }) { return <main className="basic-page page-shell"><span className="eyebrow">RENTNEARBY</span><h1>{title}</h1><p className="basic-lede">{text}</p><p>This page will be completed as the corresponding product workflow is implemented. No transaction or account action is available in this development preview.</p><Link to="/" className="text-link"><ArrowLeft size={16}/> Back home</Link></main> }
