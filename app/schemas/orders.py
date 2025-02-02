from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.schemas.products import ProductBase

class BaseConfig:
    from_attributes = True

class OrderItemBase(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    subtotal: float
    product: ProductBase

    class Config(BaseConfig):
        pass

class OrderBase(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    shipping_address: str
    created_at: datetime
    order_items: List[OrderItemBase]

    class Config(BaseConfig):
        pass

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    shipping_address: str
    cart_id: int  # We'll use this to convert cart to order

    class Config(BaseConfig):
        pass

class OrderOut(BaseModel):
    message: str
    data: OrderBase

    class Config(BaseConfig):
        pass

class OrdersOut(BaseModel):
    message: str
    data: List[OrderBase]

    class Config(BaseConfig):
        pass
