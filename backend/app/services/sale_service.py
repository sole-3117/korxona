from sqlalchemy.orm import Session
from ..models import Sale, SaleItem, Product, AuditLog
from ..schemas.sale import SaleCreate

def create_sale(db: Session, sale_in: SaleCreate, user_id: int):
    total = 0
    for item in sale_in.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product or product.stock < item.quantity:
            raise ValueError(f"Mahsulot {product.name} yetarli emas")
        product.stock -= item.quantity
        total += item.price * item.quantity
    total -= sale_in.discount_amount

    db_sale = Sale(user_id=user_id, total_amount=total, discount_amount=sale_in.discount_amount, payment_type=sale_in.payment_type)
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)

    for item in sale_in.items:
        db_item = SaleItem(sale_id=db_sale.id, product_id=item.product_id, quantity=item.quantity, price=item.price)
        db.add(db_item)
        # Log
        log = AuditLog(user_id=user_id, action="sotuv", details=f"Sotuv ID: {db_sale.id}")
        db.add(log)
    db.commit()
    return db_sale

def get_products(db: Session, search: str = ""):
    query = db.query(Product)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    return [{"id": p.id, "name": p.name, "price": p.price, "stock": p.stock} for p in query.all()]
