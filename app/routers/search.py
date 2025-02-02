from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.services.search import SearchService
from app.schemas.search import SearchResponse

router = APIRouter(tags=["Search"], prefix="/search")

# @router.post("/", response_model=SearchResponse)
# async def search_products(
#     db: Session = Depends(get_db),
#     text_query: Optional[str] = None,
#     image: UploadFile = File(None)
#     # image: UploadFile = File(
#     #     default = None,
#     #     description="Upload an image file to search similar products",
#     #     media_type="image/*"
#     # )
# ):
    
#     return await SearchService.search_products(db, text_query, image)

@router.post("/text", response_model=SearchResponse)
async def search_products_by_text(
    text_query: str = Form(...),
    db: Session = Depends(get_db)
):
    if not text_query:
        raise HTTPException(
            status_code=400,
            detail="Text query must not be empty"
        )
    return await SearchService.search_products_by_text(db, text_query)

@router.post("/image", response_model=SearchResponse)
async def search_products_by_image(
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not image:
        raise HTTPException(
            status_code=400,
            detail="Image file must be provided"
        )
    return await SearchService.search_products_by_image(db, image)