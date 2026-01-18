from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import auth, sales, expenses, inventory, reports, receipts
from .config import settings

app = FastAPI(title="POS Telegram UZ", description="Real do'kon POS tizimi")

# DB yaratish
Base.metadata.create_all(bind=engine)

# CORS (Telegram WebApp uchun)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Keyinchalik cheklash
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static fayllar (frontend)
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(sales.router, prefix="/api/sales", tags=["Sotuv"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["Xarajat"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["Ombor"])
app.include_router(reports.router, prefix="/api/reports", tags=["Hisobot"])
app.include_router(receipts.router, prefix="/api/receipts", tags=["Chek"])

@app.get("/")
async def root():
    return {"xabar": "POS Tizimi ishga tushdi! Telegram WebApp orqali kirish."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
