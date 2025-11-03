# server_app.py
# FastAPI backend for Korxona mini app
# Endpoints:
#  GET /api/data            -> returns current data JSON
#  POST /api/data?mode=merge|replace  -> import data (from frontend or bot)
#  POST /api/export         -> create export file and (optionally) send to telegram chat_id
#  POST /api/import-file    -> accept multipart file upload (used by bot when user uploads file to bot)
#  Static files not served here (frontend on GH Pages). Enable CORS.

import os
import json
import time
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import pathlib
import requests

APP_DIR = pathlib.Path(__file__).parent.resolve()
DATA_FILE = APP_DIR / "data.json"
EXPORT_DIR = APP_DIR / "exports"
EXPORT_DIR.mkdir(exist_ok=True)

BOT_TOKEN = os.environ.get("BOT_TOKEN")  # used to send export file to user
BACKEND_PORT = int(os.environ.get("PORT", 8000))

DEFAULT_DATA = {
    "version": "0.2.2025",
    "products": [],
    "users": {
        # initial super admin; change password after first login
        "superadmin": {"password": "superpass", "role": "super"}
    },
    "changeHistory": []
}

app = FastAPI(title="Korxona Backend API")

# Allow frontend from anywhere (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_data():
    if not DATA_FILE.exists():
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA.copy()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Error loading data:", e)
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA.copy()

def save_data(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

@app.get("/api/data")
def api_get_data():
    d = load_data()
    return JSONResponse(content=d)

@app.post("/api/data")
def api_post_data(payload: dict):
    """
    Replace full dataset or merge incoming dataset.
    Expects JSON body and optional query param mode=merge|replace
    """
    mode = "merge"
    # check query param manually via request: but FastAPI easier with Form. For simplicity, client should include "mode" key
    if isinstance(payload, dict) and "mode" in payload:
        mode = payload.pop("mode")
    data = load_data()
    if mode == "replace":
        # replace everything with incoming payload (except ensure version)
        payload.setdefault("version", DEFAULT_DATA["version"])
        save_data(payload)
        return {"status": "ok", "action": "replaced", "version": payload.get("version")}
    # merge mode: merge products (by id) + users + history
    incoming = payload
    existing = data
    existing_products_ids = {p.get("id") for p in existing.get("products", [])}
    for p in incoming.get("products", []):
        if p.get("id") not in existing_products_ids:
            existing.setdefault("products", []).append(p)
    # merge users (overwrite existing keys)
    existing_users = existing.get("users", {})
    incoming_users = incoming.get("users", {})
    existing_users.update(incoming_users)
    existing["users"] = existing_users
    existing["changeHistory"] = (existing.get("changeHistory", []) or []) + (incoming.get("changeHistory", []) or [])
    # add import log
    existing.setdefault("changeHistory", []).append({"at": int(time.time()*1000), "by": "import_api", "action": "merged import"})
    save_data(existing)
    return {"status": "ok", "action": "merged"}

@app.post("/api/export")
def api_export_and_send(chat_id: Optional[int] = None):
    """
    Create export JSON file and optionally send to a Telegram chat_id (if BOT_TOKEN provided and chat_id provided).
    Returns JSON with file URL (download) and result.
    """
    data = load_data()
    filename = f"korxona_export_{data.get('version','v')}_{int(time.time())}.json"
    filepath = EXPORT_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    result = {"status":"ok", "file": f"/api/download/{filename}"}
    # If bot token and chat_id provided, send file by Telegram sendDocument
    if BOT_TOKEN and chat_id:
        tg_send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        try:
            with open(filepath, "rb") as doc:
                files = {"document": (filename, doc)}
                resp = requests.post(tg_send_url, data={"chat_id": str(chat_id)}, files=files, timeout=30)
            if resp.status_code == 200:
                result["sent_to_chat"] = True
            else:
                result["sent_to_chat"] = False
                result["tg_response"] = resp.text
        except Exception as e:
            result["sent_to_chat"] = False
            result["error"] = str(e)
    return JSONResponse(content=result)

@app.get("/api/download/{fname}")
def api_download(fname: str):
    fp = EXPORT_DIR / fname
    if not fp.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=str(fp), filename=fname, media_type='application/json')

@app.post("/api/import-file")
async def api_import_file(file: UploadFile = File(...)):
    """
    Accept a JSON file upload (from the bot). Merge it into data.json.
    """
    content = await file.read()
    try:
        incoming = json.loads(content.decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
    # perform merge (same logic as /api/data merge)
    existing = load_data()
    existing_products_ids = {p.get("id") for p in existing.get("products", [])}
    for p in incoming.get("products", []):
        if p.get("id") not in existing_products_ids:
            existing.setdefault("products", []).append(p)
    existing_users = existing.get("users", {})
    incoming_users = incoming.get("users", {})
    existing_users.update(incoming_users)
    existing["users"] = existing_users
    existing["changeHistory"] = (existing.get("changeHistory",[]) or []) + (incoming.get("changeHistory", []) or [])
    existing.setdefault("changeHistory", []).append({"at": int(time.time()*1000), "by": "import_file", "action": "imported via bot"})
    save_data(existing)
    return {"status":"ok", "merged": True}

# For quick healthcheck
@app.get("/health")
def health():
    return {"status":"ok"}