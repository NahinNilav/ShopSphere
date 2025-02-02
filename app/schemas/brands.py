from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BrandBase(BaseModel):
    id: int
    name: str
    description: Optional[str]
    logo: Optional[str]
    website: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class BrandCreate(BaseModel):
    name: str
    description: Optional[str] = None
    logo: Optional[str] = None
    website: Optional[str] = None
    is_active: bool = True

class BrandUpdate(BrandCreate):
    pass

class BrandOut(BaseModel):
    message: str
    data: BrandBase

class BrandsOut(BaseModel):
    message: str
    data: List[BrandBase]

class BrandDelete(BaseModel):
    message: str
    data: BrandBase
