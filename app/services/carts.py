from sqlalchemy.orm import Session
from app.models.models import Cart, CartItem, Product
from app.schemas.carts import CartUpdate, CartCreate
from app.services.products import ProductService
from app.utils.responses import ResponseHandler
from sqlalchemy.orm import joinedload
from app.core.security import get_current_user


class CartService:
    @staticmethod
    def _prepare_cart_response(cart):
        """Transform cart data to include full image URLs for products"""
        cart_dict = dict(cart.__dict__)
        

        cart_dict['cart_items'] = []
        
        if hasattr(cart, 'cart_items'):
            for item in cart.cart_items:
                item_dict = dict(item.__dict__)
                if item.product:
                    product_dict = ProductService._prepare_product_response(item.product)
                    product_dict['category'] = {
                        'id': item.product.category.id,
                        'name': item.product.category.name
                    } if item.product.category else None
                    item_dict['product'] = product_dict
                cart_dict['cart_items'].append(item_dict)
        
        return cart_dict
    
    # # Get All Carts
    # @staticmethod
    # def get_all_carts(token, db: Session, page: int, limit: int):
    #     user_id = get_current_user(token)
    #     carts = db.query(Cart).filter(Cart.user_id == user_id).offset((page - 1) * limit).limit(limit).all()
    #     message = f"Page {page} with {limit} carts"
    #     # Transform each cart to include full image URLs for products
    #     transformed_carts = [CartService._prepare_cart_response(cart) for cart in carts]
    #     return ResponseHandler.success(message, transformed_carts)

    @staticmethod
    def get_all_carts(token, db: Session, page: int, limit: int):
        user_id = get_current_user(token)
        
        carts = (db.query(Cart)
                .filter(Cart.user_id == user_id)
                .options(
                    joinedload(Cart.cart_items)
                    .joinedload(CartItem.product)
                    .joinedload(Product.category)
                )
                .offset((page - 1) * limit)
                .limit(limit)
                .all())
        

        transformed_carts = [CartService._prepare_cart_response(cart) for cart in carts]
        return {"message": f"Page {page} with {limit} carts", "data": transformed_carts}


    # # Get A Cart By ID
    # @staticmethod
    # def get_cart(token, db: Session, cart_id: int):
    #     user_id = get_current_user(token)
    #     cart = db.query(Cart).filter(Cart.id == cart_id, Cart.user_id == user_id).first()
    #     if not cart:
    #         ResponseHandler.not_found_error("Cart", cart_id)
    #     return ResponseHandler.get_single_success("cart", cart_id, cart)

    @staticmethod
    def get_cart(token, db: Session, cart_id: int):
        user_id = get_current_user(token)
        
        cart = (db.query(Cart)
               .filter(Cart.id == cart_id, Cart.user_id == user_id)
               .options(
                   joinedload(Cart.cart_items)
                   .joinedload(CartItem.product)
                   .joinedload(Product.category)
               )
               .first())
               
        if not cart:
            ResponseHandler.not_found_error("Cart", cart_id)
        
        transformed_cart = CartService._prepare_cart_response(cart)
        
        return ResponseHandler.get_single_success("cart", cart_id, transformed_cart)

    # # Create a new Cart
    # @staticmethod
    # def create_cart(token, db: Session, cart: CartCreate):
    #     user_id = get_current_user(token)
    #     cart_dict = cart.model_dump()

    #     cart_items_data = cart_dict.pop("cart_items", [])
    #     cart_items = []
    #     total_amount = 0
    #     for item_data in cart_items_data:
    #         product_id = item_data['product_id']
    #         quantity = item_data['quantity']

    #         product = db.query(Product).filter(Product.product_id == product_id).first()
    #         if not product:
    #             return ResponseHandler.not_found_error("Product", product_id)

    #         subtotal = quantity * product.price * (1 - (product.discount_percentage / 100))
    #         cart_item = CartItem(product_id=product_id, quantity=quantity, subtotal=subtotal)
    #         total_amount += subtotal

    #         cart_items.append(cart_item)
    #     cart_db = Cart(cart_items=cart_items, user_id=user_id, total_amount=total_amount, **cart_dict)
    #     db.add(cart_db)
    #     db.commit()
    #     db.refresh(cart_db)
    #     return ResponseHandler.create_success("Cart", cart_db.id, cart_db)

    # # Update Cart & CartItem
    # @staticmethod
    # def update_cart(token, db: Session, cart_id: int, updated_cart: CartUpdate):
    #     user_id = get_current_user(token)

    #     cart = db.query(Cart).filter(Cart.id == cart_id, Cart.user_id == user_id).first()
    #     if not cart:
    #         return ResponseHandler.not_found_error("Cart", cart_id)

    #     # Delete existing cart_items
    #     db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()

    #     for item in updated_cart.cart_items:
    #         product_id = item.product_id
    #         quantity = item.quantity

    #         product = db.query(Product).filter(Product.product_id == product_id).first()
    #         if not product:
    #             return ResponseHandler.not_found_error("Product", product_id)

    #         subtotal = quantity * product.price * (1 - (product.discount_percentage / 100))

    #         cart_item = CartItem(
    #             cart_id=cart_id,
    #             product_id=product_id,
    #             quantity=quantity,
    #             subtotal=subtotal
    #         )
    #         db.add(cart_item)

    #     cart.total_amount = sum(item.subtotal for item in cart.cart_items)

    #     db.commit()
    #     db.refresh(cart)
    #     return ResponseHandler.update_success("cart", cart.id, cart)

    @staticmethod
    def create_cart(token, db: Session, cart: CartCreate):
        user_id = get_current_user(token)
        
        # Check if user already has an active cart
        existing_cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        
        total_amount = 0
        if existing_cart:
            # Use existing cart
            db_cart = existing_cart
        else:
            db_cart = Cart(user_id=user_id, total_amount=total_amount)
            db.add(db_cart)
            db.flush()

        
        for cart_item in cart.cart_items:
            product = db.query(Product).filter(Product.product_id == cart_item.product_id).first()
            if not product:
                ResponseHandler.not_found_error("Product", cart_item.product_id)

            price = product.price * (1 - (product.discount_percentage / 100))
            subtotal = price * cart_item.quantity

            existing_item = db.query(CartItem).filter(
                CartItem.cart_id == db_cart.id,
                CartItem.product_id == cart_item.product_id
            ).first()

            if existing_item:
                existing_item.quantity += cart_item.quantity
                existing_item.subtotal = price * existing_item.quantity
            else:
                db_cart_item = CartItem(
                    cart_id=db_cart.id,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    subtotal=subtotal
                )
                db.add(db_cart_item)

            total_amount += subtotal

        db_cart.total_amount = total_amount
        db.commit()
        db.refresh(db_cart)

        transformed_cart = CartService._prepare_cart_response(db_cart)
        return ResponseHandler.create_success("Cart", db_cart.id, transformed_cart)

    
    @staticmethod
    def update_cart(token, db: Session, cart_id: int, updated_cart: CartUpdate):
        user_id = get_current_user(token)
        
        # Check if cart exists and belongs to user
        cart = db.query(Cart).filter(Cart.id == cart_id, Cart.user_id == user_id).first()
        if not cart:
            ResponseHandler.not_found_error("Cart", cart_id)

        # Delete existing cart items
        db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()

        # Reset total amount
        total_amount = 0


        for cart_item in updated_cart.cart_items:
            product = db.query(Product).filter(Product.product_id == cart_item.product_id).first()
            if not product:
                ResponseHandler.not_found_error("Product", cart_item.product_id)

            price = product.price * (1 - (product.discount_percentage / 100))
            subtotal = price * cart_item.quantity

            existing_item = db.query(CartItem).filter(
                CartItem.cart_id == cart_id,
                CartItem.product_id == cart_item.product_id
            ).first()

            if existing_item:
                existing_item.quantity += cart_item.quantity
                existing_item.subtotal = price * existing_item.quantity
            else:
                db_cart_item = CartItem(
                    cart_id=cart_id,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    subtotal=subtotal
                )
                db.add(db_cart_item)

            total_amount += subtotal

        cart.total_amount = total_amount
        db.commit()
        db.refresh(cart)

        transformed_cart = CartService._prepare_cart_response(cart)
        return ResponseHandler.update_success("Cart", cart_id, transformed_cart)


    # Delete Both Cart and CartItems
    @staticmethod
    def delete_cart(token, db: Session, cart_id: int):
        user_id = get_current_user(token)
        cart = (
            db.query(Cart)
            .options(joinedload(Cart.cart_items).joinedload(CartItem.product))
            .filter(Cart.id == cart_id, Cart.user_id == user_id)
            .first()
        )
        if not cart:
            ResponseHandler.not_found_error("Cart", cart_id)

        for cart_item in cart.cart_items:
            db.delete(cart_item)

        db.delete(cart)
        db.commit()
        return ResponseHandler.delete_success("Cart", cart_id, cart)
