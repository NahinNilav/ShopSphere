from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class BaseConfig:
    from_attributes = True

class FeedbackCreate(BaseModel):
    product_id: int
    liked: bool
    rating: Optional[float] = None

    @validator("rating")
    def validate_rating(cls, v):
        if v is not None and (v < 0 or v > 5):
            raise ValueError("Rating must be between 0 and 5")
        return v

class FeedbackBase(BaseModel):
    id: int
    user_id: int
    product_id: int
    liked: bool
    rating: Optional[float]
    created_at: datetime

    class Config(BaseConfig):
        pass

class FeedbackOut(BaseModel):
    message: str
    data: FeedbackBase

    class Config(BaseConfig):
        pass
    