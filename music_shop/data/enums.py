import enum


class OrderStatus(enum.StrEnum):
    NEW = "NEW"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class DeliveryMethod(enum.StrEnum):
    DELIVERY = "DELIVERY"
    PICKUP = "PICKUP"


class AssemblyOption(enum.StrEnum):
    REQUIRED = "REQUIRED"
    NOT_REQUIRED = "NOT_REQUIRED"
