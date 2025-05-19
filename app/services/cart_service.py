from sqlalchemy.orm import Session
from ..models.order import CartItem
from ..models.product import Product
from ..schemas.order import CartItemCreate, Cart

def get_cart(db: Session, user_id: int) -> Cart:
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    total_amount = 0
    if cart_items:
        total_amount = sum(item.product.price * item.quantity for item in cart_items if item.product)
    return Cart(items=cart_items, total_amount=total_amount)

def add_to_cart(db: Session, user_id: int, item_in: CartItemCreate) -> CartItem:
    product = db.query(Product).filter(Product.id == item_in.product_id).first()
    if not product:
        raise ValueError("Sản phẩm không tồn tại")
    if product.stock < item_in.quantity:
        raise ValueError(f"Sản phẩm '{product.name}' không đủ số lượng trong kho (còn {product.stock})")
    
    cart_item = db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.product_id == item_in.product_id
    ).first()
    
    if cart_item:
        if product.stock < (cart_item.quantity + item_in.quantity):
            raise ValueError(f"Không thể thêm. Sản phẩm '{product.name}' không đủ số lượng trong kho.")
        cart_item.quantity += item_in.quantity
    else:
        cart_item = CartItem(
            user_id=user_id,
            product_id=item_in.product_id,
            quantity=item_in.quantity
        )
        db.add(cart_item)
    
    db.commit()
    db.refresh(cart_item)
    return cart_item

def update_cart_item(db: Session, user_id: int, item_id: int, quantity: int) -> CartItem:
    cart_item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == user_id).first()
    if not cart_item:
        raise ValueError("Không tìm thấy sản phẩm trong giỏ hàng")
    
    if quantity <= 0:
        db.delete(cart_item)
        db.commit()
        # Returning a representation or None for a deleted item might be better
        # For now, let's assume the caller handles the case where item might not exist after this
        return None 
    
    product = cart_item.product # Assuming cart_item.product is loaded
    if not product:
         raise ValueError("Sản phẩm liên quan đến mục trong giỏ hàng không tồn tại.")

    if product.stock < quantity:
        raise ValueError(f"Sản phẩm '{product.name}' không đủ số lượng trong kho (còn {product.stock})")
    
    cart_item.quantity = quantity
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item

def remove_from_cart(db: Session, user_id: int, item_id: int) -> None:
    cart_item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == user_id).first()
    if cart_item:
        db.delete(cart_item)
        db.commit()
    else:
        raise ValueError("Không tìm thấy sản phẩm trong giỏ hàng để xóa") 