from fastapi import APIRouter, Depends, status
from app.core.security import get_current_user
from app.db.database import get_db
from app.services.feedback import FeedbackService
from sqlalchemy.orm import Session
from app.schemas.feedback import FeedbackCreate, FeedbackOut
from app.schemas.products import ProductsOut
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials



router = APIRouter(tags=["Feedback"], prefix="/feedback")
auth_scheme = HTTPBearer()

@router.get("/swipe", response_model=ProductsOut)
def get_products_for_swiping(
    db: Session = Depends(get_db),
    limit: int = 10
):
    products = FeedbackService.get_random_products(db, limit)
    print(products)
    return {"message": f"Random {limit} products for swiping", "data": products}

@router.post("/", response_model=FeedbackOut)
def submit_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    return FeedbackService.submit_feedback(token, db, feedback)