from pydantic import BaseModel
from typing import List

class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int
    price: float

class SaleCreate(BaseModel):
    items: List[SaleItemCreate]
    discount_amount: float = 0
    payment_type: str  # 'naqd', 'karta', 'aralash'

class Sale(BaseModel):
    id: int
    total_amount: float
    discount_amount: float
    payment_type: str

    class Config:
        from_attributes = True
