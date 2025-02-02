from sqlalchemy.orm import Session
from app.models.models import Product, Category

from fastapi import UploadFile
from app.utils.upload import upload_image, upload_multiple_images

from app.schemas.products import ProductCreate, ProductUpdate
from app.utils.responses import ResponseHandler
from app.core.config import settings

from typing import List


import json

class ProductService:
    @staticmethod
    def _get_full_image_url(relative_path: str) -> str:
        """Convert relative image path to full URL"""
        if not relative_path:
            return None
        print(f"{settings.BASE_URL}/uploads{relative_path}")
        return f"{settings.BASE_URL}/uploads{relative_path}"

    @staticmethod
    def _prepare_product_response(product):
        """Transform product data to include full image URLs"""
        product_dict = dict(product.__dict__)
        product_dict['thumbnail'] = ProductService._get_full_image_url(product.thumbnail)

        product_dict['images'] = [
            ProductService._get_full_image_url(image_path) 
            for image_path in product.images
        ] if product.images else []
        return product_dict

    @staticmethod
    def get_all_products(db: Session, page: int, limit: int, search: str = ""):
        products = db.query(Product).order_by(Product.id.asc()).filter(
            Product.title.contains(search)).limit(limit).offset((page - 1) * limit).all()
        
        products_list = [dict(product.__dict__) for product in products]

        print(products_list)
        

        transformed_products = [
            ProductService._prepare_product_response(product) 
            for product in products
        ]
        
        return {"message": f"Page {page} with {limit} products", "data": transformed_products}
    
    @staticmethod
    def get_product(db: Session, product_id: int):
        product = db.query(Product).filter(Product.product_id == product_id).first()  # Use product_id instead of id
        if not product:
            ResponseHandler.not_found_error("Product", product_id)
        

        transformed_product = ProductService._prepare_product_response(product)
        return ResponseHandler.get_single_success(product.title, product_id, transformed_product)
    
    @staticmethod
    # async def create_product(db: Session, product: ProductCreate, thumbnail: UploadFile, images: List[UploadFile]):
    #     category_exists = db.query(Category).filter(Category.id == product.category_id).first()
    #     if not category_exists:
    #         ResponseHandler.not_found_error("Category", product.category_id)

    #     # Upload thumbnail
    #     thumbnail_url = await upload_image(thumbnail)
        
    #     # Upload product images
    #     image_urls = await upload_multiple_images(images)
        
    #     # Create product with image URLs
    #     product_dict = product.model_dump()
    #     product_dict['thumbnail'] = thumbnail_url
    #     product_dict['images'] = image_urls
        
    #     db_product = Product(**product_dict)
    #     db.add(db_product)
    #     db.commit()
    #     db.refresh(db_product)
    #     return ResponseHandler.create_success(db_product.title, db_product.id, db_product)

    async def create_product(db: Session, product: ProductCreate, thumbnail: UploadFile, images: List[UploadFile]):
        
        category_exists = db.query(Category).filter(Category.id == product.category_id).first()
        if not category_exists:
            ResponseHandler.not_found_error("Category", product.category_id)

        thumbnail_url = await upload_image(thumbnail)
        image_urls = await upload_multiple_images(images)
        
        # Create product with image URLs
        product_dict = product.model_dump()
        product_dict['thumbnail'] = thumbnail_url
        product_dict['images'] = image_urls
        
        db_product = Product(**product_dict)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return ResponseHandler.create_success(db_product.title, db_product.product_id, db_product)

    @staticmethod
    async def update_product(db: Session, product_id: int, updated_product: ProductUpdate, 
                           thumbnail: UploadFile = None, images: List[UploadFile] = None):
        
        db_product = db.query(Product).filter(Product.product_id == product_id).first()
        if not db_product:
            ResponseHandler.not_found_error("Product", product_id)

        # Handle image updates
        if thumbnail:
            thumbnail_url = await upload_image(thumbnail)
            print(thumbnail_url)
            updated_product.thumbnail = thumbnail_url

        if images:
            image_urls = await upload_multiple_images(images)
            updated_product.images = image_urls

        for key, value in updated_product.model_dump().items():
            setattr(db_product, key, value)

        db.commit()
        db.refresh(db_product)
        return ResponseHandler.update_success(db_product.title, db_product.product_id, db_product)
    
    @staticmethod
    def delete_product(db: Session, product_id: int):
        
        db_product = db.query(Product).filter(Product.product_id == product_id).first()
        if not db_product:
            ResponseHandler.not_found_error("Product", product_id)
        db.delete(db_product)
        db.commit()
        return ResponseHandler.delete_success(db_product.title, db_product.product_id, db_product)