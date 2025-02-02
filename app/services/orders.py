from sqlalchemy.orm import Session
from app.models.models import Order, OrderItem, Cart, CartItem, User, Product
from app.schemas.orders import OrderCreate
from app.utils.responses import ResponseHandler
from app.core.security import get_current_user
from fastapi import HTTPException, status

class OrderService:
    @staticmethod
    def get_all_orders(token, db: Session, page: int, limit: int):
        user_id = get_current_user(token)
        orders = db.query(Order).filter(Order.user_id == user_id)\
            .offset((page - 1) * limit).limit(limit).all()
        return {"message": f"Page {page} with {limit} orders", "data": orders}

    @staticmethod
    def get_order(token, db: Session, order_id: int):
        user_id = get_current_user(token)
        order = db.query(Order).filter(
            Order.id == order_id, 
            Order.user_id == user_id
        ).first()
        
        if not order:
            ResponseHandler.not_found_error("Order", order_id)
        return ResponseHandler.get_single_success("Order", order_id, order)

    @staticmethod
    def create_order(token, db: Session, order: OrderCreate):
        user_id = get_current_user(token)
        
        # Get cart
        cart = db.query(Cart).filter(
            Cart.id == order.cart_id, 
            Cart.user_id == user_id
        ).first()
        
        if not cart:
            ResponseHandler.not_found_error("Cart", order.cart_id)

        # Create order
        order_db = Order(
            user_id=user_id,
            total_amount=cart.total_amount,
            shipping_address=order.shipping_address,
            status="pending"
        )
        
        db.add(order_db)
        db.flush()  # Get order_id without committing

        cart_items_from_cart_id = db.query(CartItem).filter(
            CartItem.cart_id == order.cart_id
        ).all()

        if not cart_items_from_cart_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No items found in cart with ID: {order.cart_id}"
            )

        # Convert cart items to order items
        order_items = []
        for cart_item in cart_items_from_cart_id:
            product = db.query(Product).filter(Product.product_id == cart_item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {cart_item.product_id} not found"
                )
    
            # Create OrderItem for the cart item
            order_item = OrderItem(
                order_id=order_db.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=product.price * (1 - (product.discount_percentage / 100)),
                subtotal=cart_item.quantity * product.price * (1 - (product.discount_percentage / 100))
            )
            order_items.append(order_item)
            
            # Update stock
            product.stock -= cart_item.quantity
            if product.stock < 0:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for product {product.title}"
                )

        db.add_all(order_items)

        for cart_item in cart_items_from_cart_id:
            db.delete(cart_item)

        cart = db.query(Cart).filter(
            Cart.id == order.cart_id
        ).first()
        if cart:
            db.delete(cart)

        # Commit transaction
        db.commit()
        db.refresh(order_db)

        return ResponseHandler.create_success("Order", order_db.id, order_db)
    
    @staticmethod
    def get_user_orders(token, db: Session, user_id: int, page: int, limit: int):
        current_user_id = get_current_user(token)
        

        user = db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if current_user_id != user_id and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view other users' orders"
            )
        
        
        orders = db.query(Order).filter(Order.user_id == user_id)\
            .order_by(Order.created_at.desc())\
            .offset((page - 1) * limit)\
            .limit(limit)\
            .all()
        
        return {
            "message": f"Orders for user {user_id}, page {page} with {limit} orders per page",
            "data": orders
        }