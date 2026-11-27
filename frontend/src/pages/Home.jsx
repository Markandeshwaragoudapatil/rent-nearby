import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { ArrowRight, ArrowUpRight, Camera, Drill, Headphones, MapPin, Search, ShieldCheck, Sparkles, Clock3, Handshake, PackageCheck } from "lucide-react"
import { categories, demoProducts } from "../data/marketplace"
import ProductCard from "../components/ProductCard"
import { fetchProducts } from "../services/products"

const categoryIcons = { camera: Camera, wrench: Drill, party: Headphones }

export default function Home() {
  const [query, setQuery] = useState("")
  const [location, setLocation] = useState("Bengaluru")
  const [featured, setFeatured] = useState([])
  const [loadingFeatured, setLoadingFeatured] = useState(true)
  const [apiUnavailable, setApiUnavailable] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    let active = true
    fetchProducts({ perPage: 4 })
      .then(result => {
        if (active) {
          setFeatured(result.items)
          setApiUnavailable(false)
        }
      })
      .catch(() => {
        if (active) {
          setFeatured(demoProducts)
          setApiUnavailable(true)
        }
      })
      .finally(() => { if (active) setLoadingFeatured(false) })
    return () => { active = false }
  }, [])

  const search = event => {
    event.preventDefault()
    navigate(`/browse?q=${encodeURIComponent(query)}&locality=${encodeURIComponent(location === "Bengaluru" ? "" : location)}`)
  }

  return (
    <main>
      <section className="hero-section">
        <div className="page-shell hero-grid">
          <div className="hero-copy">
            <div className="eyebrow"><span className="eyebrow-dot"/> THE NEIGHBOURHOOD RENTAL MARKETPLACE</div>
            <h1>Don't buy it.<br/><span>Rent it.</span></h1>
            <p className="hero-description">The things you need, from the people around you. Save money, make more of what you own.</p>
            <form className="search-panel" onSubmit={search}>
              <label className="search-field"><Search size={19}/><span><small>What are you looking for?</small><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Camera, drill, projector..." aria-label="What are you looking for?"/></span></label>
              <span className="search-divider"/>
              <label className="search-field location-field"><MapPin size={19}/><span><small>Where?</small><input value={location} onChange={event => setLocation(event.target.value)} aria-label="Location"/></span></label>
              <button className="search-submit" type="submit" aria-label="Search"><ArrowRight size={21}/></button>
            </form>
            <div className="hero-note"><span className="avatar-stack"><i>R</i><i>A</i><i>K</i></span><span>Local finds. Real people. Less waste.</span></div>
          </div>
          <div className="hero-visual">
            <div className="hero-image-main"><img src="https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=1200&q=90" alt="Camera equipment ready for a creative project"/><span className="image-caption">Make room for more experiences.</span></div>
            <div className="hero-floating-card"><span className="floating-icon"><Sparkles size={18}/></span><div><b>More access, less ownership</b><small>Good gear, when you need it.</small></div></div>
            <div className="hero-stamp">SHARE<br/>MORE<span>↗</span></div>
          </div>
        </div>
        <div className="hero-bottom page-shell"><span>BUILT AROUND YOUR NEIGHBOURHOOD</span><span className="hero-location"><MapPin size={14}/> Starting in Bengaluru, India</span></div>
      </section>

      <section className="section categories-section" id="categories">
        <div className="page-shell">
          <div className="section-heading"><div><span className="eyebrow">A LITTLE OF EVERYTHING</span><h2>What do you need<br/>for <em>today?</em></h2></div><a href="/browse" className="round-link">Explore all items <ArrowUpRight size={17}/></a></div>
          <div className="category-grid">{categories.map((category, index) => { const Icon = categoryIcons[category.icon]; return <a className={`category-card category-${category.color}`} href={`/browse?category=${encodeURIComponent(category.slug)}`} key={category.name}><div className="category-number">0{index + 1}</div><div className="category-icon"><Icon size={27} strokeWidth={1.6}/></div><div><h3>{category.name}</h3><p>{category.count}</p></div><span className="category-arrow"><ArrowUpRight size={19}/></span></a> })}</div>
        </div>
      </section>

      <section className="section featured-section">
        <div className="page-shell"><div className="section-heading featured-heading"><div><span className="eyebrow">GOOD FINDS, CLOSE BY</span><h2>Popular around<br/><em>your corner.</em></h2></div><p className="section-intro">Discover useful things listed by people in your neighbourhood.</p></div>
          {apiUnavailable && <div className="demo-notice"><Sparkles size={15}/> API unavailable · Showing sample items. These are not real inventory.</div>}
          {loadingFeatured ? <p className="catalogue-status" role="status">Loading local listings…</p> :
            featured.length ? <div className="product-grid">{featured.map(product => <ProductCard product={product} key={product.id}/>)}</div> :
            <div className="empty-state"><Camera size={30}/><h2>New listings are on the way</h2><p>There are no approved items to show yet.</p></div>}
          <div className="center-action"><a href="/browse" className="button button-outline">Explore the marketplace <ArrowUpRight size={17}/></a></div>
        </div>
      </section>

      <section className="section how-section" id="how-it-works"><div className="page-shell how-layout"><div className="how-intro"><span className="eyebrow">SIMPLE AS IT SHOULD BE</span><h2>Borrow a little.<br/><em>Live a lot.</em></h2><p>From finding the right thing to bringing it back, we make sharing feel easy.</p><a href="/browse" className="text-link text-link-light">Find your next rental <ArrowUpRight size={16}/></a></div><div className="steps-list"><article className="step-card"><span className="step-icon"><Search size={22}/></span><span className="step-index">01 / DISCOVER</span><h3>Find your thing</h3><p>Explore useful things listed by people in your neighbourhood.</p></article><article className="step-card"><span className="step-icon"><Clock3 size={22}/></span><span className="step-index">02 / REQUEST</span><h3>Book your dates</h3><p>Choose when you need it and send a request to the owner.</p></article><article className="step-card"><span className="step-icon"><Handshake size={22}/></span><span className="step-index">03 / SHARE</span><h3>Pick up & enjoy</h3><p>Meet, check the item together, make something happen and return it.</p></article></div></div></section>

      <section className="owner-section"><div className="page-shell owner-banner"><div className="owner-art"><img src="https://images.unsplash.com/photo-1492619375914-88005aa9e8fb?auto=format&fit=crop&w=900&q=85" alt="Creative equipment ready to be shared"/><div className="owner-art-note"><PackageCheck size={18}/> Give good things a second life.</div></div><div className="owner-copy"><span className="eyebrow">YOUR STUFF HAS PLANS</span><h2>That thing you<br/>barely use? <em>Someone needs it.</em></h2><p>Turn the gear sitting on your shelf into a little extra income. You stay in control of your listing, availability and requests.</p><a href="/list-item" className="button button-dark">Become an owner <ArrowUpRight size={17}/></a><div className="owner-footnote"><ShieldCheck size={16}/> Clear bookings. Transparent terms. Your call.</div></div></div></section>

      <section className="trust-section"><div className="page-shell trust-inner"><div><span className="eyebrow">SHARING WORKS WHEN TRUST DOES</span><h2>Good neighbours.<br/><em>Good experiences.</em></h2></div><div className="trust-points"><div><ShieldCheck size={22}/><span><b>Know who you're renting from</b><small>Transparent owner profiles and verification status.</small></span></div><div><PackageCheck size={22}/><span><b>Know what you're getting</b><small>Clear descriptions and condition checks at handover.</small></span></div><div><Handshake size={22}/><span><b>Know where you stand</b><small>Upfront pricing, booking records and support for issues.</small></span></div></div></div></section>
      <section className="final-cta"><div className="page-shell final-cta-inner"><span className="eyebrow">MAKE ROOM FOR MORE</span><h2>Need less stuff.<br/><em>Get more done.</em></h2><a href="/browse" className="button button-light">Find something nearby <ArrowRight size={18}/></a></div></section>
    </main>
  )
}
