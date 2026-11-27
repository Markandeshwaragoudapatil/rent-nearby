import { describe, expect, it } from 'vitest'
import { categories, demoProducts } from './marketplace'

describe('development catalogue', () => {
  it('contains the three MVP discovery categories', () => {
    expect(categories.map(category => category.name)).toEqual(['Electronics', 'Tools', 'Event equipment'])
  })
  it('labels every sample listing with a demo-only id', () => {
    expect(demoProducts.length).toBeGreaterThan(0)
    expect(demoProducts.every(product => product.id.startsWith('demo-'))).toBe(true)
  })
  it('uses non-negative integer rupee prices', () => {
    expect(demoProducts.every(product => Number.isInteger(product.price) && product.price >= 0)).toBe(true)
  })
})
