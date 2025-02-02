from fastapi import APIRouter, Depends, Query, status
from app.db.database import get_db
from app.services.wishlists import WishlistService
from sqlalchemy.orm import Session
from app.schemas.wishlists import WishlistItemCreate, WishlistItemOut, WishlistItemsOut
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

router = APIRouter(tags=["Wishlist"], prefix="/wishlist")
auth_scheme = HTTPBearer()

@router.get("/", response_model=WishlistItemsOut)
def get_wishlist(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    return WishlistService.get_wishlist(token, db, page, limit)


@router.post("/", response_model=WishlistItemOut)
def add_to_wishlist(
    wishlist_item: WishlistItemCreate,
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    return WishlistService.add_to_wishlist(token, db, wishlist_item)


@router.delete("/{product_id}", response_model=WishlistItemOut)
def remove_from_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    return WishlistService.remove_from_wishlist(token, db, product_id)
