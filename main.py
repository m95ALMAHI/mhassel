import os
import secrets
import urllib.parse
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None

app = FastAPI(title="بورصة محاصيل السودان")

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# بيانات دخول لوحة التحكم
security = HTTPBasic()
ADMIN_USERNAME = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASS", "sd_crops_2026")

def authenticate_admin(credentials: HTTPBasicCredentials = Depends(security)):
    is_user_correct = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    is_pass_correct = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (is_user_correct and is_pass_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="بيانات الدخول غير صحيحة",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# --- 1. الرئيسية ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    orders = []
    if engine:
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM market_orders ORDER BY id DESC"))
                raw_orders = [dict(row._mapping) for row in result]
                for order in raw_orders:
                    msg = f"السلام عليكم، أود الاستفسار عن عرض المحصول: {order['crop_name']}\nالكمية: {order['quantity']}\nالسعر: {order['price_per_unit']} SDG"
                    order['wa_link'] = f"https://wa.me/{order['phone']}?text={urllib.parse.quote(msg)}"
                    orders.append(order)
        except Exception as e:
            print(f"Error fetching orders: {e}")

    return templates.TemplateResponse("index.html", {"request": request, "orders": orders})

# --- 2. صفحة الإدارة المستقلة ---
@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, username: str = Depends(authenticate_admin)):
    transactions = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT * FROM transactions ORDER BY id DESC"))
                transactions = [dict(row._mapping) for row in res]
        except Exception as e:
            print(f"Admin fetch error: {e}")

    return templates.TemplateResponse("admin.html", {"request": request, "transactions": transactions})

# --- 3. مسار إضافة عرض/طلب مباشر من الصفحة الرئيسية ---
@app.post("/add-order")
async def add_order(
    crop_name: str = Form(...),
    order_type: str = Form(...),
    quantity: str = Form(...),
    price_per_unit: float = Form(...),
    state: str = Form(...),
    phone: str = Form(...)
):
    if engine:
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO market_orders (crop_name, order_type, quantity, price_per_unit, state, phone)
                    VALUES (:crop, :type, :qty, :price, :state, :phone)
                """), {
                    "crop": crop_name, "type": order_type, "qty": quantity,
                    "price": price_per_unit, "state": state, "phone": phone
                })
                conn.commit()
        except Exception as e:
            print(f"Error adding order: {e}")

    return RedirectResponse(url="/", status_code=303)

# --- 4. مسار إضافة نشرة من الأدمن ---
@app.post("/add-price")
async def process_add_price(
    crop_name: str = Form(...),
    order_type: str = Form("SELL"),
    quantity: str = Form(...),
    price_per_unit: float = Form(...),
    state: str = Form(...),
    phone: str = Form(...),
    username: str = Depends(authenticate_admin)
):
    if engine:
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO market_orders (crop_name, order_type, quantity, price_per_unit, state, phone)
                    VALUES (:crop, :type, :qty, :price, :state, :phone)
                """), {
                    "crop": crop_name, "type": order_type, "qty": quantity,
                    "price": price_per_unit, "state": state, "phone": phone
                })
                conn.commit()
        except Exception as e:
            print(f"Error adding price from admin: {e}")

    return RedirectResponse(url="/admin", status_code=303)
