from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from app.models.models import ProductFeedback, Product
from app.schemas.feedback import FeedbackCreate
from app.utils.responses import ResponseHandler
from app.core.security import get_current_user
from typing import List
from app.services.products import ProductService

class FeedbackService:
    @staticmethod
    def get_random_products(db: Session, limit: int = 10) -> List[Product]:
        deck_products = db.query(Product).order_by(func.random()).limit(limit).all()
        transformed_products = [
            ProductService._prepare_product_response(product) 
            for product in deck_products
        ]

        return transformed_products
    
    def get_random_products_recomm(db: Session, limit: int) -> List[Product]:
        deck_products = db.query(Product).order_by(func.random()).limit(limit).all()

        transformed_products = [
            ProductService._prepare_product_response(product) 
            for product in deck_products
        ]

        return transformed_products

    @staticmethod
    def submit_feedback(token, db: Session, feedback: FeedbackCreate):
        user_id = get_current_user(token)

        if not user_id:
            print("Send token for retrieving user id")
        

        existing_feedback = db.query(ProductFeedback).filter(
            ProductFeedback.user_id == user_id,
            ProductFeedback.product_id == feedback.product_id
        ).first()

        if existing_feedback:
            existing_feedback.liked = feedback.liked
            existing_feedback.rating = feedback.rating
            db.commit()
            db.refresh(existing_feedback)
            return ResponseHandler.update_success("Feedback", existing_feedback.id, existing_feedback)

        # Create new feedback
        db_feedback = ProductFeedback(
            user_id=user_id,
            product_id=feedback.product_id,
            liked=feedback.liked,
            rating=feedback.rating
        )
        
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        return ResponseHandler.create_success("Feedback", db_feedback.id, db_feedback)

    @staticmethod
    def get_popular_products(db: Session, brand_id: int, limit: int = 5):
        """Get popular products based on likes and ratings"""
        return db.query(
            Product,
            func.count(ProductFeedback.id).label('likes_count'),
            func.avg(ProductFeedback.rating).label('average_rating')
        )\
            .join(ProductFeedback)\
            .filter(
                Product.brand_id == brand_id,
                ProductFeedback.liked == True  # Only count positive likes
            )\
            .group_by(Product.id)\
            .order_by(
                func.count(ProductFeedback.id).desc(),
                func.avg(ProductFeedback.rating).desc()
            )\
            .limit(limit)\
            .all() 