from pydantic import BaseModel
from datetime import datetime
from typing import List
from app.schemas.products import ProductBase

class BaseConfig:
    from_attributes = True

class WishlistItemBase(BaseModel):
    id: int
    user_id: int
    product_id: int
    created_at: datetime
    product: ProductBase

    class Config(BaseConfig):
        pass

class WishlistItemCreate(BaseModel):
    product_id: int

class WishlistItemOut(BaseModel):
    message: str
    data: WishlistItemBase

    class Config(BaseConfig):
        pass

class WishlistItemsOut(BaseModel):
    message: str
    data: List[WishlistItemBase]

    class Config(BaseConfig):
        pass