# Database design

## ER diagram

```mermaid
erDiagram
  USERS ||--o{ USER_ADDRESSES : has
  USERS ||--o{ PRODUCTS : owns
  CATEGORIES ||--o{ PRODUCTS : classifies
  PRODUCTS ||--o{ PRODUCT_IMAGES : has
  PRODUCTS ||--|| RENTAL_PRICING : priced_by
  PRODUCTS ||--o{ AVAILABILITY_RULES : schedules
  USERS ||--o{ BOOKINGS : rents
  PRODUCTS ||--o{ BOOKINGS : reserved_for
  BOOKINGS ||--o{ PAYMENTS : paid_by
  BOOKINGS ||--o{ BOOKING_EVENTS : records
  BOOKINGS ||--o| REVIEWS : receives
  USERS ||--o{ REVIEWS : writes
  BOOKINGS ||--o{ DISPUTES : may_raise
  USERS ||--o{ DISPUTES : raises
  USERS ||--o{ AUDIT_LOGS : performs

  USERS { uuid id PK string email UK string password_hash string role }
  USER_ADDRESSES { uuid id PK uuid user_id FK string city string pincode decimal latitude decimal longitude }
  CATEGORIES { uuid id PK string name UK string slug UK boolean is_active }
  PRODUCTS { uuid id PK uuid owner_id FK uuid category_id FK string title string status string condition }
  PRODUCT_IMAGES { uuid id PK uuid product_id FK string asset_id string image_url boolean is_primary }
  RENTAL_PRICING { uuid id PK uuid product_id FK bigint hourly_price_paise bigint daily_price_paise bigint deposit_paise }
  AVAILABILITY_RULES { uuid id PK uuid product_id FK date start_date date end_date boolean is_available }
  BOOKINGS { uuid id PK uuid renter_id FK uuid product_id FK date start_date date end_date bigint rental_paise bigint deposit_paise bigint fee_paise string status }
  PAYMENTS { uuid id PK uuid booking_id FK bigint amount_paise string provider_order_id string provider_payment_id string status }
  BOOKING_EVENTS { uuid id PK uuid booking_id FK uuid actor_id FK string from_status string to_status }
  REVIEWS { uuid id PK uuid booking_id FK uuid reviewer_id FK int rating string comment }
  DISPUTES { uuid id PK uuid booking_id FK uuid raised_by FK string status string description }
  AUDIT_LOGS { uuid id PK uuid actor_id FK string action string resource_type uuid resource_id }
```

## Important constraints and indexes

- `users.email` unique (case-insensitive normalized email); phone unique only when verified and present.
- `categories.slug` unique.
- `rental_pricing.product_id` unique; prices and deposit non-negative; at least one hourly/daily price must be positive.
- `products.owner_id`, `category_id` indexed; search index on approved/active listings.
- `bookings.start_date < bookings.end_date`; amounts non-negative; renter cannot book own product.
- PostgreSQL exclusion constraint on `(product_id WITH =, daterange(start_date,end_date,'[)') WITH &&)` for blocking statuses. Implement partial GiST index with `btree_gist`; verify generated SQL in migration.
- `payments.provider_payment_id` unique when non-null; webhook event ID unique.
- One review per completed booking; rating 1–5.
- Foreign keys use restrictive deletes for financial and booking records; archive users/products rather than destructive cascades.
- Store money as integer paise, never floating point. Store UTC timestamps; date-only rental periods are interpreted in Asia/Kolkata for the pilot.

## Additional tables beyond the original brief

`booking_events`, `audit_logs`, `payment_webhook_events`, `owner_verifications`, `reports`, and `wishlist_items` support auditability, idempotency, moderation and the renter experience. Exact columns will be implemented alongside the relevant feature.
