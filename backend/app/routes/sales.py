from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.sale import SaleCreate, Sale
from ..services.sale_service import create_sale, get_products
from ..models.user import User
from ..services.auth_service import get_current_user
from typing import List

router = APIRouter()

@router.get("/products", response_model=List[dict])
async def list_products(search: str = "", current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_products(db, search)

@router.post("/create", response_model=Sale)
async def make_sale(sale: SaleCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_sale(db, sale, current_user.id)
