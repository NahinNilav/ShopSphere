from fastapi import Form, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import requests
from app.models.models import Product
from app.services.products import ProductService
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SearchService:
    # @staticmethod
    # async def search_products(
    #     db: Session,
    #     text_query: Optional[str] = None,
    #     image: Optional[UploadFile] = File(None)
    # ) -> dict:
        
    #     # Debug: Initial input parameters
    #     print(f"Received text_query: {text_query}")
    #     print(f"Received image: {image.filename if image else 'No image provided'}")

    #     if not text_query and not image:
    #         raise HTTPException(
    #             status_code=400,
    #             detail="Either text_query or image must be provided"
    #         )

    #     try:
    #         files = {}
    #         data = {}
            
    #         if text_query:
    #             data['text_query'] = text_query
    #             # Debug: Text query being sent
    #             print(f"Text query data: {data}")

    #         if image:
    #             file_content = await image.read()
    #             files['image'] = (
    #                 image.filename,
    #                 file_content,
    #                 image.content_type
    #             )
    #             # Debug: File details
    #             print(f"File prepared with filename: {image.filename}, size: {len(file_content)} bytes, content_type: {image.content_type}")

    #         print(f"Data to external API: {data}")
    #         print(f"Files to external API: {files.keys()}")

    #         # Make request to external search API
    #         response = requests.post(
    #             f"{settings.SEARCH_API_URL}/search",
    #             data=data,
    #             files=files
    #         )
            
    #         print(f"External API response status: {response.status_code}")
    #         print(f"External API response content: {response.text}")

    #         if response.status_code != 200:
    #             raise HTTPException(
    #                 status_code=response.status_code,
    #                 detail="External search API error"
    #             )

    #         # Get product paths from response
    #         product_paths = response.json().get('paths', [])
    #         print(f"Product paths from external API: {product_paths}")

    #         if not product_paths:
    #             return {
    #                 "message": "No matching products found",
    #                 "data": []
    #             }

    #         products = db.query(Product).filter(
    #             Product.thumbnail.in_(product_paths)
    #         ).all()
    #         print(f"Products retrieved: {[product.thumbnail for product in products]}")


    #         transformed_products = []
    #         for product in products:
    #             product_dict = {
    #                 "id": product.id,
    #                 "title": product.title,
    #                 "description": product.description,
    #                 "price": product.price,
    #                 "thumbnail": ProductService._get_full_image_url(product.thumbnail),
    #                 "images": [ProductService._get_full_image_url(img) for img in product.images] if product.images else [],
    #                 # Add other fields as needed
    #             }
    #             transformed_products.append(product_dict)

    #         return {
    #             "message": "Search results retrieved successfully",
    #             "data": transformed_products
    #         }
            
    #         # # Transform products to include full image URLs
    #         # transformed_products = [
    #         #     ProductService._prepare_product_response(product)
    #         #     for product in products
    #         # ]

    #         # # Debug: Transformed product details
    #         # print(f"Transformed products: {transformed_products}")

    #         # return {
    #         #     "message": "Search results retrieved successfully",
    #         #     "data": transformed_products
    #         # }

    #     except Exception as e:
    #         print(f"Error during search operation: {str(e)}")
    #         logger.error(f"Search error: {str(e)}")
    #         raise HTTPException(
    #             status_code=500,
    #             detail=f"Search operation failed: {str(e)}"
    #         )
        
    @staticmethod
    async def search_products_by_text(
        db: Session,
        text_query: str
    ) -> dict:
        try:
            # Prepare data for the external API
            data = {'text_query': text_query}
            print(f"Text query data: {data}")

            # Make request to the external search API
            response = requests.post(
                f"{settings.SEARCH_API_URL}/search",
                data=data
            )

            print(f"External API response status: {response.status_code}")
            print(f"External API response content: {response.text}")

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="External search API error"
                )

            return SearchService._process_search_results(db, response)

        except Exception as e:
            print(f"Error during text search operation: {str(e)}")
            logger.error(f"Text search error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Text search operation failed: {str(e)}"
            )

    @staticmethod
    async def search_products_by_image(
        db: Session,
        image: UploadFile
    ) -> dict:
        try:
            file_content = await image.read()
            files = {
                'image': (
                    image.filename,
                    file_content,
                    image.content_type
                )
            }
            print(f"File prepared with filename: {image.filename}, size: {len(file_content)} bytes, content_type: {image.content_type}")

            response = requests.post(
                f"{settings.SEARCH_API_URL}/search",
                files=files
            )

            print(f"External API response status: {response.status_code}")
            print(f"External API response content: {response.text}")

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="External search API error"
                )

            return SearchService._process_search_results(db, response)

        except Exception as e:
            print(f"Error during image search operation: {str(e)}")
            logger.error(f"Image search error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Image search operation failed: {str(e)}"
            )

    @staticmethod
    def _process_search_results(db: Session, response: requests.Response) -> dict:
        product_paths = response.json().get('paths', [])
        print(f"Product paths from external API: {product_paths}")

        if not product_paths:
            return {
                "message": "No matching products found",
                "data": []
            }


        products = db.query(Product).filter(
            Product.thumbnail.in_(product_paths)
        ).all()
        print(f"Products retrieved: {[product.thumbnail for product in products]}")

        transformed_products = []
        for product in products:
            product_dict = {
                "id": product.product_id,
                "title": product.title,
                "description": product.description,
                "price": product.price,
                "thumbnail": ProductService._get_full_image_url(product.thumbnail),
                "images": [ProductService._get_full_image_url(img) for img in product.images] if product.images else [],
            }
            transformed_products.append(product_dict)

        return {
            "message": "Search results retrieved successfully",
            "data": transformed_products
        }
    