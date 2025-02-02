from sqlalchemy.orm import Session
from app.models.models import Wishlist, Product
from app.schemas.wishlists import WishlistItemCreate
from app.services.products import ProductService
from app.utils.responses import ResponseHandler
from app.core.security import get_current_user
from fastapi import HTTPException, status

class WishlistService:
    @staticmethod
    def get_wishlist(token, db: Session, page: int, limit: int):
        print(token)
        user_id = get_current_user(token)
        wishlist_items = db.query(Wishlist).filter(Wishlist.user_id == user_id).offset((page - 1) * limit).limit(limit).all()
        transformed_items = []
        for item in wishlist_items:
            item_dict = dict(item.__dict__)
            if item.product:
                item_dict['product'] = ProductService._prepare_product_response(item.product)
            transformed_items.append(item_dict)  
        return {"message": f"Page {page} with {limit} wishlist items", "data": transformed_items}

    @staticmethod
    def add_to_wishlist(token, db: Session, wishlist_item: WishlistItemCreate):
        user_id = get_current_user(token)
        
        product = db.query(Product).filter(Product.product_id == wishlist_item.product_id).first()
        if not product:
            ResponseHandler.not_found_error("Product", wishlist_item.product_id)

        existing_item = db.query(Wishlist).filter(
            Wishlist.user_id == user_id,
            Wishlist.product_id == wishlist_item.product_id
        ).first()

        if existing_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product already in wishlist"
            )


        db_wishlist_item = Wishlist(
            user_id=user_id,
            product_id=wishlist_item.product_id
        )
        
        db.add(db_wishlist_item)
        db.commit()
        db.refresh(db_wishlist_item)
        
        return ResponseHandler.create_success("Wishlist item", db_wishlist_item.id, db_wishlist_item)

    @staticmethod
    def remove_from_wishlist(token, db: Session, product_id: int):
        user_id = get_current_user(token)
        
        wishlist_item = db.query(Wishlist).filter(
            Wishlist.user_id == user_id,
            Wishlist.product_id == product_id
        ).first()

        if not wishlist_item:
            ResponseHandler.not_found_error("Wishlist item", product_id)

        db.delete(wishlist_item)
        db.commit()
        
        return ResponseHandler.delete_success("Wishlist item", wishlist_item.id, wishlist_item)
