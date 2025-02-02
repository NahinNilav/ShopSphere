from fastapi import APIRouter, Depends, Query, status
from app.db.database import get_db
from app.services.orders import OrderService
from sqlalchemy.orm import Session
from app.schemas.orders import OrderCreate, OrderOut, OrdersOut
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

router = APIRouter(tags=["Orders"], prefix="/orders")
auth_scheme = HTTPBearer()

@router.get("/", response_model=OrdersOut)
def get_all_orders(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    return OrderService.get_all_orders(token, db, page, limit)

@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    return OrderService.get_order(token, db, order_id)


@router.get("/user/{user_id}", response_model=OrdersOut)
def get_user_orders(
    user_id: int,
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    return OrderService.get_user_orders(token, db, user_id, page, limit)

@router.post("/", response_model=OrderOut)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    return OrderService.create_order(token, db, order)
