from pydantic import BaseModel

class ExpenseCreate(BaseModel):
    type: str
    amount: float
    note: str = None

class Expense(BaseModel):
    id: int
    type: str
    amount: float
    note: str

    class Config:
        from_attributes = True
