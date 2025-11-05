from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os

app = FastAPI()

# Static va template fayllarni ulash
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DATA_FILE = "data/products.json"

# Ma'lumotlar fayli mavjud bo'lmasa, yaratamiz
if not os.path.exists("data"):
    os.mkdir("data")
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/products")
async def get_products():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return JSONResponse(content=data)

@app.post("/api/add_product")
async def add_product(name: str = Form(...), price: str = Form(None), note: str = Form(None)):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    new_product = {
        "name": name,
        "price": price,
        "note": note
    }
    data.append(new_product)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {"status": "success", "message": "Mahsulot qo‘shildi!"}
