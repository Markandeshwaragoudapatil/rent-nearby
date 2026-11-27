class UserRole:
    RENTER = "RENTER"
    OWNER = "OWNER"
    ADMIN = "ADMIN"

class ProductCondition:
    VALUES = {"NEW", "LIKE_NEW", "GOOD", "FAIR"}

class ProductStatus:
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"

class BookingStatus:
    VALUES = {"PENDING", "ACCEPTED", "REJECTED", "PAYMENT_PENDING", "CONFIRMED", "ACTIVE", "COMPLETED", "CANCELLED", "DISPUTED"}
