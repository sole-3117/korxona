# app.py
import os, io, json
from fastapi import FastAPI, Request, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from auth_utils import create_access_token, verify_token, hash_password, verify_password
from models import SessionLocal, init_db, User, Product, History
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

init_db()

app = FastAPI(title="Korxona v0.2.2025")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# serve frontend
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# helper: auth dependency
def get_current_user(token: Optional[str] = None, db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    data = verify_token(token)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid token")
    username = data.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# login
@app.post("/api/login")
async def api_login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    # log history
    db.add(History(user=user.username, action="login", ts=datetime.utcnow()))
    db.commit()
    return {"access_token": token, "token_type": "bearer", "role": user.role, "username": user.username}

# register admin (super only)
@app.post("/api/add_admin")
async def add_admin(username: str = Form(...), password: str = Form(...), token: Optional[str] = Form(None), db: Session = Depends(get_db)):
    cur = get_current_user(token, db)
    if cur.role != "super":
        raise HTTPException(status_code=403, detail="Only super admin")
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="User exists")
    u = User(username=username, password_hash=hash_password(password), role="admin")
    db.add(u)
    db.add(History(user=cur.username, action=f"add_admin:{username}", ts=datetime.utcnow()))
    db.commit()
    return {"ok": True}

# promote admin -> super
@app.post("/api/promote")
async def promote_user(username: str = Form(...), token: Optional[str] = Form(None), db: Session = Depends(get_db)):
    cur = get_current_user(token, db)
    if cur.role != "super":
        raise HTTPException(status_code=403, detail="Only super admin")
    u = db.query(User).filter(User.username == username).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.role = "super"
    db.add(History(user=cur.username, action=f"promote:{username}", ts=datetime.utcnow()))
    db.commit()
    return {"ok": True}

# products CRUD
@app.get("/api/products")
async def get_products(db: Session = Depends(get_db)):
    ps = db.query(Product).order_by(Product.created_at.desc()).all()
    return [{"id":p.id,"name":p.name,"price":p.price,"note":p.note,"image":p.image,"created_at":p.created_at.isoformat()} for p in ps]

@app.post("/api/products")
async def add_product(name: str = Form(...), price: Optional[str] = Form(None), note: Optional[str] = Form(None), image: Optional[UploadFile] = File(None), token: Optional[str] = Form(None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    # only admin or super allowed
    if user.role not in ("admin","super"):
        raise HTTPException(status_code=403, detail="Not allowed")
    image_path = None
    if image:
        content = await image.read()
        # save base64 or file: to keep simple save to exports folder
        fname = f"static/uploads/{int(datetime.utcnow().timestamp())}_{image.filename}"
        os.makedirs(os.path.dirname(fname), exist_ok=True)
        with open(fname, "wb") as f:
            f.write(content)
        image_path = "/" + fname
    p = Product(name=name, price=price, note=note, image=image_path)
    db.add(p)
    db.add(History(user=user.username, action=f"add_product:{name}", ts=datetime.utcnow()))
    db.commit()
    return {"ok": True, "id": p.id}

@app.put("/api/products/{pid}")
async def edit_product(pid: int, name: str = Form(...), price: Optional[str] = Form(None), note: Optional[str] = Form(None), token: Optional[str] = Form(None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if user.role not in ("admin","super"):
        raise HTTPException(status_code=403, detail="Not allowed")
    p = db.query(Product).filter(Product.id == pid).first()
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    p.name = name
    p.price = price
    p.note = note
    db.add(History(user=user.username, action=f"edit_product:{pid}", ts=datetime.utcnow()))
    db.commit()
    return {"ok": True}

@app.delete("/api/products/{pid}")
async def delete_product(pid: int, token: Optional[str] = Form(None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if user.role != "super":
        raise HTTPException(status_code=403, detail="Only super can delete")
    p = db.query(Product).filter(Product.id == pid).first()
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(p)
    db.add(History(user=user.username, action=f"delete_product:{pid}", ts=datetime.utcnow()))
    db.commit()
    return {"ok": True}

# profile endpoints
@app.get("/api/profile")
async def profile(token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    return {"username": user.username, "role": user.role, "created_at": user.created_at.isoformat()}

@app.post("/api/change_password")
async def change_password(old: str = Form(...), new: str = Form(...), token: Optional[str] = Form(None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not verify_password(old, user.password_hash):
        raise HTTPException(status_code=400, detail="Old password wrong")
    user.password_hash = hash_password(new)
    db.add(History(user=user.username, action="change_password", ts=datetime.utcnow()))
    db.commit()
    return {"ok": True}

# history (super only)
@app.get("/api/history")
async def get_history(token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if user.role != "super":
        raise HTTPException(status_code=403, detail="Only super")
    hs = db.query(History).order_by(History.ts.desc()).limit(500).all()
    return [{"user":h.user,"action":h.action,"ts":h.ts.isoformat()} for h in hs]

# export: produce JSON file
@app.get("/api/export")
async def api_export(db: Session = Depends(get_db), token: Optional[str] = None):
    user = get_current_user(token, db)
    if user.role != "super":
        raise HTTPException(status_code=403, detail="Only super")
    products = db.query(Product).all()
    users = db.query(User).all()
    history = db.query(History).all()
    data = {
        "version":"0.2.2025",
        "products":[{"id":p.id,"name":p.name,"price":p.price,"note":p.note,"image":p.image,"created_at":p.created_at.isoformat()} for p in products],
        "users":[{"username":u.username,"role":u.role} for u in users],
        "history":[{"user":h.user,"action":h.action,"ts":h.ts.isoformat()} for h in history]
    }
    s = json.dumps(data, ensure_ascii=False, indent=2)
    b = io.BytesIO(s.encode("utf-8"))
    b.seek(0)
    fname = f"korxona_export_{int(datetime.utcnow().timestamp())}.json"
    return FileResponse(b, media_type="application/json", filename=fname)

# import JSON (from uploaded file)
@app.post("/api/import")
async def api_import(file: UploadFile = File(...), token: Optional[str] = Form(None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if user.role != "super":
        raise HTTPException(status_code=403, detail="Only super")
    raw = await file.read()
    try:
        incoming = json.loads(raw.decode("utf-8"))
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    # Merge products that are not present by id or name
    for it in incoming.get("products", []):
        if not db.query(Product).filter(Product.name == it.get("name")).first():
            p = Product(name=it.get("name"), price=it.get("price"), note=it.get("note"), image=it.get("image"))
            db.add(p)
    # users: create if not exists (no password imported)
    for u in incoming.get("users", []):
        if not db.query(User).filter(User.username==u.get("username")).first():
            newu = User(username=u.get("username"), password_hash=hash_password("changeme"), role=u.get("role","admin"))
            db.add(newu)
    db.add(History(user=user.username, action="import_data", ts=datetime.utcnow()))
    db.commit()
    return {"ok": True}

# health
@app.get("/health")
async def health():
    return {"status":"ok"}
