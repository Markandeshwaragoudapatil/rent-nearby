import { useEffect, useState } from "react"
import { Link, useParams, useSearchParams } from "react-router-dom"
import { ArrowLeft, ArrowUpRight, Camera, Search } from "lucide-react"
import { demoProducts } from "../data/marketplace"
import ProductCard from "../components/ProductCard"
import { fetchProduct, fetchProducts } from "../services/products"

function filterDemoProducts(query, category, locality) {
  return demoProducts.filter(product =>
    (!query || `${product.name} ${product.category} ${product.location}`.toLowerCase().includes(query.toLowerCase())) &&
    (!category || product.category.toLowerCase().includes(category.toLowerCase()) || category.toLowerCase().includes(product.category.toLowerCase())) &&
    (!locality || product.location.toLowerCase().includes(locality.toLowerCase()))
  )
}

export function Browse() {
  const [searchParams] = useSearchParams()
  const query = searchParams.get("q") || ""
  const category = searchParams.get("category") || ""
  const locality = searchParams.get("locality") || ""
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [apiUnavailable, setApiUnavailable] = useState(false)

  useEffect(() => {
    let active = true
    setLoading(true)
    fetchProducts({ q: query, category, locality, perPage: 30 })
      .then(result => {
        if (active) {
          setProducts(result.items)
          setApiUnavailable(false)
        }
      })
      .catch(() => {
        if (active) {
          setProducts(filterDemoProducts(query, category, locality))
          setApiUnavailable(true)
        }
      })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [query, category, locality])

  return (
    <main className="basic-page page-shell">
      <span className="eyebrow">THE LOCAL FINDS</span>
      <h1>Explore what's <em>around.</em></h1>
      <p className="basic-lede">Discover useful things listed by people in your neighbourhood.</p>
      {apiUnavailable && <div className="demo-notice"><Search size={15}/> API unavailable · Showing clearly labelled sample items instead.</div>}
      {loading ? <p className="catalogue-status" role="status">Finding items nearby…</p> :
        products.length ? <div className="product-grid browse-grid">{products.map(product => <ProductCard product={product} key={product.id}/>)}</div> :
        <div className="empty-state"><Camera size={30}/><h2>No listings found</h2><p>{apiUnavailable ? "Try another search in the sample catalogue." : "There are no approved live listings matching this search yet."}</p><Link to="/browse" className="button button-dark">Clear search</Link></div>}
    </main>
  )
}

export function ProductDetail() {
  const { id } = useParams()
  const isDemo = id?.startsWith("demo-")
  const demoProduct = demoProducts.find(product => product.id === id)
  const [product, setProduct] = useState(isDemo ? demoProduct : null)
  const [loading, setLoading] = useState(!isDemo)
  const [apiUnavailable, setApiUnavailable] = useState(false)

  useEffect(() => {
    if (isDemo) {
      setProduct(demoProduct || null)
      setLoading(false)
      return
    }
    let active = true
    setLoading(true)
    fetchProduct(id)
      .then(result => { if (active) { setProduct(result); setApiUnavailable(false) } })
      .catch(() => { if (active) { setProduct(null); setApiUnavailable(true) } })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [id, isDemo, demoProduct])

  if (loading) return <main className="basic-page page-shell"><p role="status">Loading item details…</p></main>
  if (!product) return <main className="basic-page page-shell"><h1>Item not found</h1><p>{apiUnavailable ? "The listing could not be loaded from RentNearby." : "This item is not part of the preview catalogue."}</p><Link to="/browse" className="text-link"><ArrowLeft size={16}/> Back to explore</Link></main>

  const price = Number.isInteger(product.pricePaise) ? product.pricePaise / 100 : product.price
  return (
    <main className="basic-page page-shell detail-page">
      <Link to="/browse" className="text-link"><ArrowLeft size={16}/> Back to explore</Link>
      <div className="detail-layout">
        {product.image ? <img src={product.image} alt={product.name}/> : <div className="detail-placeholder"><Camera size={48}/></div>}
        <div>
          <span className={product.isLive ? "live-label" : "demo-label"}>{product.isLive ? "LIVE LISTING" : "DEMO ITEM · NOT BOOKABLE"}</span>
          <span className="eyebrow">{product.category}</span>
          <h1>{product.name}</h1>
          <p className="product-location">{product.location}, Bengaluru</p>
          <p>{product.description}</p>
          {product.condition && <p>Condition: {product.condition.replaceAll("_", " ").toLowerCase()}</p>}
          <h2>₹{price.toLocaleString("en-IN", { maximumFractionDigits: 2 })} <small>/ {product.unit}</small></h2>
          <p className="detail-disclaimer">{product.isLive ? "This listing is visible from the catalogue. Booking and payment are not enabled yet." : "This is illustrative content. It is not live inventory and cannot be booked."}</p>
          <Link to="/browse" className="button button-dark">Continue exploring <ArrowUpRight size={17}/></Link>
        </div>
      </div>
    </main>
  )
}

export function InfoPage({ title, text }) {
  return <main className="basic-page page-shell"><span className="eyebrow">RENTNEARBY</span><h1>{title}</h1><p className="basic-lede">{text}</p><p>This page will be completed as the corresponding product workflow is implemented. No transaction or account action is available here yet.</p><Link to="/" className="text-link"><ArrowLeft size={16}/> Back home</Link></main>
}
