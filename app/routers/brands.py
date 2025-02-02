from fastapi import APIRouter, Depends, Query, status, File, UploadFile
from app.db.database import get_db
from app.services.brands import BrandService
from sqlalchemy.orm import Session
from app.schemas.brands import BrandCreate, BrandUpdate, BrandOut, BrandsOut, BrandDelete
from app.schemas.filters import ProductFilters
from app.core.security import check_admin_role
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from typing import List, Optional

router = APIRouter(tags=["Brands"], prefix="/brands")
auth_scheme = HTTPBearer()

@router.get("/", response_model=BrandsOut)
def get_all_brands(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str = Query("", description="Search brands by name")
):
    return BrandService.get_all_brands(db, page, limit, search)

@router.get("/{brand_id}", response_model=BrandOut)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    return BrandService.get_brand(db, brand_id)

@router.post("/", response_model=BrandOut, dependencies=[Depends(check_admin_role)])
async def create_brand(
    brand: BrandCreate = Depends(),
    logo: UploadFile = File(None),
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    return await BrandService.create_brand(db, brand, logo)

@router.put("/{brand_id}", response_model=BrandOut, dependencies=[Depends(check_admin_role)])
async def update_brand(
    brand_id: int,
    brand: BrandUpdate = Depends(),
    logo: UploadFile = File(None),
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    return await BrandService.update_brand(db, brand_id, brand, logo)

@router.delete("/{brand_id}", response_model=BrandDelete, dependencies=[Depends(check_admin_role)])
def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    return BrandService.delete_brand(db, brand_id)

# No filter implementation
# @router.get("/{brand_id}/products")
# def get_brand_products(
#     brand_id: int,
#     db: Session = Depends(get_db),
#     page: int = Query(1, ge=1, description="Page number"),
#     limit: int = Query(10, ge=1, le=100, description="Items per page")
# ):
#     return BrandService.get_brand_products(db, brand_id, page, limit)

@router.get("/{brand_id}/products")
def get_brand_products(
    brand_id: int,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    gender: Optional[str] = Query(None, description="Filter by gender (men/women/unisex)"),
    category_ids: Optional[List[int]] = Query(None, description="Filter by category IDs"),
    min_price: Optional[int] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[int] = Query(None, ge=0, description="Maximum price"),
    sizes: Optional[List[str]] = Query(None, description="Filter by sizes"),
    in_stock_only: bool = Query(False, description="Show only in-stock products"),
    include_popular: Optional[bool] = False
):
    filters = ProductFilters(
        gender=gender,
        category_ids=category_ids,
        min_price=min_price,
        max_price=max_price,
        sizes=sizes,
        in_stock_only=in_stock_only
    )
    return BrandService.get_brand_products(db, brand_id, page, limit, filters, include_popular)
