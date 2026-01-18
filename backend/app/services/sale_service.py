from sqlalchemy.orm import Session
from ..models import Sale, SaleItem, Product
from ..schemas.sale import SaleCreate

def create_sale(db: Session, sale_in: SaleCreate, user_id: int):
    # Ombor kamaytirish
    for item in sale_in.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product.stock < item.quantity:
            raise ValueError("Ombor yetarli emas")
        product.stock -= item.quantity
    
    # Sotuv yaratish
    db_sale = Sale(**sale_in.dict(), user_id=user_id)
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    
    # Elementlar
    for item in sale_in.items:
        db_item = SaleItem(sale_id=db_sale.id, **item.dict())
        db.add(db_item)
    
    db.commit()
    # Log qo'shish
    # PDF chek yaratish (pdf_generator.py chaqirish)
    return db_sale
