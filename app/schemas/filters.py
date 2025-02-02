from pydantic import BaseModel, validator
from typing import List, Optional

class ProductFilters(BaseModel):
    gender: Optional[str] = None
    category_ids: Optional[List[int]] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    sizes: Optional[List[str]] = None
    in_stock_only: bool = False

    @validator("gender")
    def validate_gender(cls, v):
        if v is not None:
            allowed_genders = ["men", "women", "unisex"]
            if v.lower() not in allowed_genders:
                raise ValueError("gender must be one of: men, women, unisex")
            return v.lower()
        return v
    