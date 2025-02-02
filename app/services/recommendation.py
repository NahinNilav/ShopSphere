import pandas as pd
import numpy as np
from requests import Session
from sqlalchemy import func
from app.services.feedback import FeedbackService
from app.models.models import ProductFeedback, Product
from app.services.products import ProductService

class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.metadata = pd.read_csv('/path/to/metadata2.csv')  

    def get_recommendations(self, user_id: int, top_k: int = 3):
        liked_feedback = self.db.query(ProductFeedback).filter(
            ProductFeedback.user_id == user_id,
            ProductFeedback.liked == True
        ).order_by(ProductFeedback.created_at.desc()).limit(10).all()

        if not liked_feedback:
            return FeedbackService.get_random_products_recomm(self.db, 20)

        liked_product_ids = [feedback.product_id for feedback in liked_feedback]
        products = self.db.query(Product).filter(Product.product_id.in_(liked_product_ids)).all()


        liked_images = []
        indices = []
        for product in products:
            thumbnail_path = product.thumbnail  
            image_name = thumbnail_path.split('/')[-1]  # Extract number.jpg
            matched_rows = self.metadata[self.metadata['image_path'].str.endswith(image_name)]
            if not matched_rows.empty:
                liked_images.append(matched_rows['image_path'].values[0])  # Get the image path
                indices.append(matched_rows.index[0])  # Get the index in metadata

        
        print(liked_images) 
        print(indices)

        image_embeddings = np.load('/path/to//image_embeddings.npy')  
        text_embeddings = np.load('/path/to//text_embeddings.npy')  
        
        similar_idx_all_liked = []
        for index in indices:
            similarity_scores = image_embeddings[index].dot(image_embeddings.T)
            top_indices = np.argsort(similarity_scores)[::-1][:top_k]
            similar_idx_all_liked.extend(top_indices)
        
        similar_idx_all_liked = list(dict.fromkeys(similar_idx_all_liked))


        result_paths = [
            self.metadata.loc[idx, "image_path"].replace("/content/new/", "/products/") 
            for idx in similar_idx_all_liked
        ]
        
        print(result_paths)

        ### The key of product data is id which should be product_id for consistent naming. Value okay ###

        # Retrieve product data based on the result_paths
        products_data = self.db.query(Product).filter(Product.thumbnail.in_(result_paths)).all()
        products_info = [
            {
                "id": product.product_id,
                "title": product.title,
                "description": product.description,
                "price": product.price,
                "thumbnail": ProductService._get_full_image_url(product.thumbnail),
                "images": [ProductService._get_full_image_url(img) for img in product.images] if product.images else [],
            }
            for product in products_data
        ]

        min_recommendations = 20
        if len(products_info) < min_recommendations:
            existing_product_ids = {product['product_id'] for product in products_info}
            additional_count = min_recommendations - len(products_info)
            

            ### Business logic replaced by random function ###  
            additional_products = (
                self.db.query(Product)
                .filter(Product.product_id.notin_(existing_product_ids))
                .order_by(func.random())
                .limit(additional_count)
                .all()
            )

            additional_products_info = [
                {
                    "id": product.product_id,
                    "title": product.title,
                    "description": product.description,
                    "price": product.price,
                    "thumbnail": ProductService._get_full_image_url(product.thumbnail),
                    "images": [ProductService._get_full_image_url(img) for img in product.images] if product.images else [],
                }
                for product in additional_products
            ]

            products_info.extend(additional_products_info)


        if not similar_idx_all_liked:
            return {
                "recommendations": []
            }

        else:
            return {
                "liked_images": liked_images,
                # "recommendations": result_paths,
                "products": products_info  
            }