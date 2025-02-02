from pydantic import BaseModel, validator, Field
from datetime import datetime
from typing import List, Optional, ClassVar
from enum import Enum
from app.schemas.categories import CategoryBase
from app.schemas.brands import BrandBase


# Base Models
class BaseConfig:
    from_attributes = True


# Too many mandatory fields 
# class ProductBase(BaseModel):
#     id: int
#     title: str
#     description: Optional[str]
#     price: int

#     @validator("discount_percentage", pre=True)
#     def validate_discount_percentage(cls, v):
#         if v < 0 or v > 100:
#             raise ValueError("discount_percentage must be between 0 and 100")
#         return v

#     discount_percentage: float
#     rating: float
#     stock: int
#     brand: str
#     thumbnail: str
#     images: List[str]
#     is_published: bool
#     created_at: datetime
#     category_id: int
#     category: CategoryBase

#     class Config(BaseConfig):
#         pass


# Create Product
# class ProductCreate(ProductBase):
#     id: ClassVar[int]
#     category: ClassVar[CategoryBase]

#     class Config(BaseConfig):
#         pass


# Before including brands information 
# class ProductBase(BaseModel):
#     title: str
#     description: str
#     price: int
#     discount_percentage: float = 0.0  # Default to 0
#     rating: Optional[float] = None
#     stock: int = 0  # Default to 0
#     brand: str
#     thumbnail: Optional[str] = None
#     images: List[str] = []  # Default to empty list
#     is_published: bool = True  # Default to True
#     category_id: int

#     @validator("discount_percentage", pre=True)
#     def validate_discount_percentage(cls, v):
#         if v < 0 or v > 100:
#             raise ValueError("discount_percentage must be between 0 and 100")
#         return v

#     class Config(BaseConfig):
#         pass


# class ProductCreate(BaseModel):
#     title: str
#     description: Optional[str] = None
#     price: int
#     discount_percentage: float = 0.0
#     stock: int = 0
#     brand: str
#     category_id: int
#     is_published: bool = True

#     class Config(BaseConfig):
#         pass


# # Update Product
# class ProductUpdate(ProductCreate):
#     pass


# # Get Products
# class ProductOut(BaseModel):
#     message: str
#     data: ProductBase

#     class Config(BaseConfig):
#         pass


# class ProductsOut(BaseModel):
#     message: str
#     data: List[ProductBase]

#     class Config(BaseConfig):
#         pass


# # Delete Product
# class ProductDelete(ProductBase):
#     category: ClassVar[CategoryBase]


# class ProductOutDelete(BaseModel):
#     message: str
#     data: ProductDelete


# After including brands information

class GenderEnum(str, Enum):
    MEN = "men"
    WOMEN = "women"
    UNISEX = "unisex"

class SizeEnum(str, Enum):
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"
    XXL = "XXL"
    # Add shoe sizes if needed
    SIZE_38 = "38"
    SIZE_39 = "39"
    SIZE_40 = "40"
    SIZE_41 = "41"
    SIZE_42 = "42"
    SIZE_43 = "43"
    SIZE_44 = "44"

class ProductBase(BaseModel):
    product_id: int
    title: str
    description: str
    price: int
    discount_percentage: float = 0.0  
    rating: Optional[float] = None
    stock: int = 0  
    brand: Optional[BrandBase] = None
    thumbnail: Optional[str] = None
    images: List[str] = []  
    is_published: bool = True 
    category_id: int
    brand_id: int
    gender: str
    sizes: List[SizeEnum]

    @validator("gender")
    def validate_gender(cls, v):
        allowed_genders = ["men", "women", "unisex"]
        if v.lower() not in allowed_genders:
            raise ValueError("gender must be one of: men, women, unisex")
        return v.lower()

    @validator("discount_percentage", pre=True)
    def validate_discount_percentage(cls, v):
        if v < 0 or v > 100:
            raise ValueError("discount_percentage must be between 0 and 100")
        return v


    # use_enum_values = True in a Config class ensures 
    # that Pydantic works with Enum values instead of Enum objects 
    # during validation and serialization
    class Config(BaseConfig):
         use_enum_values = True
        # pass


class ProductCreate(BaseModel):
    product_id: int  
    title: str
    description: Optional[str] = None
    price: int
    discount_percentage: float = 0.0
    stock: int = 0
    brand_id: int  
    category_id: int
    is_published: bool = True

    thumbnail: Optional[str] = None
    images: List[str] = []  

    gender: GenderEnum
    sizes: List[SizeEnum]


    @validator("gender")
    def validate_gender(cls, v):
        allowed_genders = ["men", "women", "unisex"]
        if v.lower() not in allowed_genders:
            raise ValueError("gender must be one of: men, women, unisex")
        return v.lower()
    

    @validator("discount_percentage", pre=True)
    def validate_discount_percentage(cls, v):
        if v < 0 or v > 100:
            raise ValueError("discount_percentage must be between 0 and 100")
        return v

    class Config(BaseConfig):
         use_enum_values = True
        # pass


# Update Product
class ProductUpdate(ProductCreate):
    pass


# Get Products
class ProductOut(BaseModel):
    message: str
    data: ProductBase  

    class Config(BaseConfig):
        pass


class ProductsOut(BaseModel):
    message: str
    data: List[ProductBase]  

    class Config(BaseConfig):
        pass


# Delete Product
class ProductDelete(ProductBase):
    category: ClassVar[CategoryBase]
    brand: ClassVar[BrandBase]  


class ProductOutDelete(BaseModel):
    message: str
    data: ProductDelete