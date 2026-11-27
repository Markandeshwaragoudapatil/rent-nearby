import { apiRequest } from "./api"

export function normalizeProduct(product) {
  const primaryImage = product.images?.find(image => image.is_primary) || product.images?.[0]
  const dailyPrice = product.pricing?.daily_price_paise || 0
  const hourlyPrice = product.pricing?.hourly_price_paise || 0
  const pricePaise = dailyPrice || hourlyPrice
  return {
    id: String(product.id),
    name: product.title,
    category: product.category?.name || "Other",
    pricePaise,
    unit: dailyPrice ? "day" : "hour",
    location: product.locality || product.city || "Bengaluru",
    image: primaryImage?.url || null,
    tag: "Live listing",
    description: product.description || "",
    condition: product.condition,
    isLive: true,
  }
}

export async function fetchProducts(filters = {}) {
  const params = new URLSearchParams()
  if (filters.q) params.set("q", filters.q)
  if (filters.locality) params.set("locality", filters.locality)
  if (filters.category) params.set("category", filters.category)
  params.set("page", String(filters.page || 1))
  params.set("per_page", String(filters.perPage || 20))
  const result = await apiRequest(`/products?${params.toString()}`)
  return { ...result, items: (result.items || []).map(normalizeProduct) }
}

export async function fetchProduct(productId) {
  const result = await apiRequest(`/products/${encodeURIComponent(productId)}`)
  return normalizeProduct(result)
}
