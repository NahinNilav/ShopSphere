from sqlalchemy.orm import Session
from app.models.models import Brand, Product
from app.schemas.brands import BrandCreate, BrandUpdate
from app.utils.responses import ResponseHandler
from fastapi import UploadFile
from app.utils.upload import upload_image
from app.core.config import settings
from app.services.products import ProductService
from app.schemas.filters import ProductFilters
from sqlalchemy import and_
from app.services.feedback import FeedbackService


class BrandService:
    @staticmethod
    def _get_full_image_url(relative_path: str) -> str:
        """Convert relative image path to full URL"""
        if not relative_path:
            return None
        return f"{settings.BASE_URL}/uploads{relative_path}"

    @staticmethod
    def _prepare_brand_response(brand):
        """Transform brand data to include full image URL"""
        brand_dict = dict(brand.__dict__)
        brand_dict['logo'] = BrandService._get_full_image_url(brand.logo)
        return brand_dict

    @staticmethod
    def get_all_brands(db: Session, page: int, limit: int, search: str = ""):
        brands = db.query(Brand).order_by(Brand.id.asc()).filter(
            Brand.name.contains(search)).limit(limit).offset((page - 1) * limit).all()
        
        # Transform full image URLs
        transformed_brands = [
            BrandService._prepare_brand_response(brand) 
            for brand in brands
        ]
        
        return {"message": f"Page {page} with {limit} brands", "data": transformed_brands}

    @staticmethod
    def get_brand(db: Session, brand_id: int):
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            ResponseHandler.not_found_error("Brand", brand_id)
            
        transformed_brand = BrandService._prepare_brand_response(brand)
        return ResponseHandler.get_single_success(brand.name, brand_id, transformed_brand)

    @staticmethod
    async def create_brand(db: Session, brand: BrandCreate, logo: UploadFile = None):
        brand_dict = brand.model_dump()
        
        if logo:
            logo_url = await upload_image(logo)
            brand_dict['logo'] = logo_url

        db_brand = Brand(**brand_dict)
        db.add(db_brand)
        db.commit()
        db.refresh(db_brand)
        

        transformed_brand = BrandService._prepare_brand_response(db_brand)
        return ResponseHandler.create_success(db_brand.name, db_brand.id, transformed_brand)

    @staticmethod
    async def update_brand(db: Session, brand_id: int, brand: BrandUpdate, logo: UploadFile = None):
        db_brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not db_brand:
            ResponseHandler.not_found_error("Brand", brand_id)

        if logo:
            logo_url = await upload_image(logo)
            brand.logo = logo_url

        for key, value in brand.model_dump().items():
            setattr(db_brand, key, value)

        db.commit()
        db.refresh(db_brand)
        

        transformed_brand = BrandService._prepare_brand_response(db_brand)
        return ResponseHandler.update_success(db_brand.name, db_brand.id, transformed_brand)

    @staticmethod
    def delete_brand(db: Session, brand_id: int):
        db_brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not db_brand:
            ResponseHandler.not_found_error("Brand", brand_id)
        db.delete(db_brand)
        db.commit()
        return ResponseHandler.delete_success(db_brand.name, db_brand.id, db_brand)

    # Old get_brand_products function 
    # @staticmethod
    # def get_brand_products(db: Session, brand_id: int, page: int, limit: int):
    #     brand = db.query(Brand).filter(Brand.id == brand_id).first()
    #     if not brand:
    #         ResponseHandler.not_found_error("Brand", brand_id)
            
    #     products = brand.products[((page - 1) * limit):(page * limit)]
    #     # Transform products to include full image URLs
    #     transformed_products = [
    #         ProductService._prepare_product_response(product) 
    #         for product in products
    #     ]
    #     return {"message": f"Products for brand {brand.name}", "data": transformed_products}
    

    # Implemented get_brand_products from stable release
    # @staticmethod
    # def get_brand_products(
    #     db: Session, 
    #     brand_id: int, 
    #     page: int, 
    #     limit: int,
    #     filters: ProductFilters = None
    # ):
    #     """
    #     Get products for a specific brand with optional filters
    #     """
    #     # First check if brand exists
    #     brand = db.query(Brand).filter(Brand.id == brand_id).first()
    #     if not brand:
    #         ResponseHandler.not_found_error("Brand", brand_id)

    #     # Base query
    #     query = db.query(Product).filter(Product.brand_id == brand_id)

    #     # Apply filters if provided
    #     if filters:
    #         if filters.gender:
    #             query = query.filter(Product.gender == filters.gender)
            
    #         if filters.category_ids:
    #             query = query.filter(Product.category_id.in_(filters.category_ids))
            
    #         if filters.min_price is not None:
    #             query = query.filter(Product.price >= filters.min_price)
            
    #         if filters.max_price is not None:
    #             query = query.filter(Product.price <= filters.max_price)
            
    #         if filters.sizes:
    #             # Filter products that have any of the requested sizes
    #             query = query.filter(Product.sizes.overlap(filters.sizes))
            
    #         if filters.in_stock_only:
    #             query = query.filter(Product.stock > 0)

    #     # Apply pagination
    #     total_items = query.count()
    #     products = query.order_by(Product.id.asc())\
    #                 .offset((page - 1) * limit)\
    #                 .limit(limit)\
    #                 .all()

    #     # Transform products to include full image URLs
    #     transformed_products = [
    #         ProductService._prepare_product_response(product) 
    #         for product in products
    #     ]
        
        
    #     return {
    #         "message": f"Products for brand {brand.name}",
    #         "data": transformed_products,
    #         "metadata": {
    #             "total_items": total_items,
    #             "page": page,
    #             "limit": limit,
    #             "total_pages": (total_items + limit - 1) // limit,
    #             "filters_applied": filters.model_dump() if filters else None
    #         }
    #     }
    
    
    @staticmethod
    def get_brand_products(
        db: Session, 
        brand_id: int, 
        page: int, 
        limit: int,
        filters: ProductFilters = None,
        include_popular: bool = False
    ):

        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            ResponseHandler.not_found_error("Brand", brand_id)

        popular_products = []
        if include_popular:
            popular_products = FeedbackService.get_popular_products(db, brand_id)

        query = db.query(Product).filter(Product.brand_id == brand_id)

        if filters:
            if filters.gender:
                query = query.filter(Product.gender == filters.gender)
            
            if filters.category_ids:
                query = query.filter(Product.category_id.in_(filters.category_ids))
            
            if filters.min_price is not None:
                query = query.filter(Product.price >= filters.min_price)
            
            if filters.max_price is not None:
                query = query.filter(Product.price <= filters.max_price)
            
            if filters.sizes:
                query = query.filter(Product.sizes.overlap(filters.sizes))
            
            if filters.in_stock_only:
                query = query.filter(Product.stock > 0)

        # Apply pagination
        total_items = query.count()
        products = query.order_by(Product.id.asc())\
                    .offset((page - 1) * limit)\
                    .limit(limit)\
                    .all()

        transformed_products = []
        
        transformed_products = [
            ProductService._prepare_product_response(product) 
            for product in products
        ]


        return {
            "message": f"Products for brand {brand.name}",
            "popular_products": [
                {
                    **ProductService._prepare_product_response(product),
                    "likes_count": int(likes_count),
                    "average_rating": float(average_rating) if average_rating else None
                }
                for product, likes_count, average_rating in popular_products
            ] if include_popular else None,

            "data": transformed_products,
            "metadata": {
                "total_items": total_items,
                "page": page,
                "limit": limit,
                "total_pages": (total_items + limit - 1) // limit,
                "filters_applied": filters.model_dump() if filters else None
            }
        }