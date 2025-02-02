from fastapi import APIRouter, Depends, Query, status, File, UploadFile, Form
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import List, Optional
from app.db.database import get_db
from app.services.products import ProductService
from sqlalchemy.orm import Session
from app.schemas.products import ProductCreate, ProductOut, ProductsOut, ProductOutDelete, ProductUpdate
from app.core.security import get_current_user, check_admin_role


router = APIRouter(tags=["Products"], prefix="/products")
auth_scheme = HTTPBearer()

# Public endpoints - anyone can view products
# Get All Products
@router.get("/", status_code=status.HTTP_200_OK, response_model=ProductsOut)
def get_all_products(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str | None = Query("", description="Search based title of products"),
):
    return ProductService.get_all_products(db, page, limit, search)


# Protected endpoints all the remaining - require Admin authentication
# Get Product By ID
@router.get("/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return ProductService.get_product(db, product_id)


# Create New Product
# @router.post(
#     "/",
#     status_code=status.HTTP_201_CREATED,
#     response_model=ProductOut,
#     dependencies=[Depends(check_admin_role)])
# async def create_product(
#     product: ProductCreate = Depends(),
#     thumbnail: UploadFile = File(...),
#     images: List[UploadFile] = File(...),
#     db: Session = Depends(get_db),
#     token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
#     return await ProductService.create_product(db, product, thumbnail, images)

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductOut,
    dependencies=[Depends(check_admin_role)])
async def create_product(
    product: ProductCreate = Depends(),
    thumbnail: UploadFile = File(...),  # Required
    product_images: List[UploadFile] = File(default=[]),  # Optional
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """
    - thumbnail: Required single image for product thumbnail
    - product_images: Optional list of additional product images
    """
    return await ProductService.create_product(db, product, thumbnail, product_images)

# Update Exist Product
@router.put(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProductOut,
    dependencies=[Depends(check_admin_role)])
async def update_product(
    product_id: int,
    product: ProductUpdate = Depends(),
    thumbnail: UploadFile = File(None),
    images: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    return await ProductService.update_product(db, product_id, product, thumbnail, images)

# Delete Product By ID
@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProductOutDelete,
    dependencies=[Depends(check_admin_role)])
def delete_product(
        product_id: int,
        db: Session = Depends(get_db)):
    return ProductService.delete_product(db, product_id)
