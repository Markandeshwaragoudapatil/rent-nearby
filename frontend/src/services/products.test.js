import { describe, expect, it } from "vitest"
import { normalizeProduct } from "./products"

describe("normalizeProduct", () => {
  it("converts paise to a rupee price and selects the primary image", () => {
    const product = normalizeProduct({
      id: "product-1",
      title: "Mirrorless camera",
      description: "Camera kit",
      condition: "LIKE_NEW",
      locality: "Indiranagar",
      city: "Bengaluru",
      category: { name: "Electronics" },
      images: [
        { url: "https://example.com/secondary.jpg", is_primary: false },
        { url: "https://example.com/primary.jpg", is_primary: true },
      ],
      pricing: { daily_price_paise: 85000, hourly_price_paise: 0 },
    })
    expect(product.name).toBe("Mirrorless camera")
    expect(product.pricePaise / 100).toBe(850)
    expect(product.unit).toBe("day")
    expect(product.image).toBe("https://example.com/primary.jpg")
    expect(product.isLive).toBe(true)
  })

  it("uses hourly pricing when a daily price is not configured", () => {
    const product = normalizeProduct({
      id: "product-2", title: "Audio recorder", category: { name: "Electronics" },
      pricing: { daily_price_paise: 0, hourly_price_paise: 2500 },
    })
    expect(product.pricePaise).toBe(2500)
    expect(product.unit).toBe("hour")
  })

  it("does not invent an image when the listing has no uploaded image", () => {
    const product = normalizeProduct({
      id: "product-3", title: "Tripod", pricing: { daily_price_paise: 10000 },
    })
    expect(product.image).toBeNull()
  })
})
