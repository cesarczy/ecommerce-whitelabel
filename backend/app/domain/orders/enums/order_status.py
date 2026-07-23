from enum import StrEnum


class OrderStatus(StrEnum):
    CREATED = "created"
    AWAITING_PAYMENT = "awaiting_payment"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
