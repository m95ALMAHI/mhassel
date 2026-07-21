import os
import urllib.parse
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None

app = FastAPI(title="بورصة محاصيل السودان")

# مجلد المرفقات لحفظ صور الإشعارات البنكية
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- 1. الصفحة الرئيسية (لوحة البورصة) ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    orders = []
    if engine:
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM market_orders ORDER BY created_at DESC"))
                raw_orders = [dict(row._mapping) for row in result]
                
                # إضافة رابط الواتساب الديناميكي لكل عرض
                for order in raw_orders:
                    msg = f"السلام عليكم، أرغب في شراء/شراء محصول: {order['crop_name']}\nالكمية: {order['quantity']}\nالسعر: {order['price_per_unit']} جنيه\nالمدينة: {order['state']}"
                    order['wa_link'] = f"https://wa.me/{order['phone']}?text={urllib.parse.quote(msg)}"
                    orders.append(order)
        except Exception as e:
            print(f"Error fetching market orders: {e}")

    return templates.TemplateResponse("index.html", {"request": request, "orders": orders})

# --- 2. إضافات العروض والطلبات للبورصة ---
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
            print(f"Error inserting order: {e}")

    return RedirectResponse(url="/", status_code=303)

# --- 3. تسجيل إشعار التحويل البنكي ---
@app.post("/submit-payment")
async def submit_payment(
    order_id: int = Form(...),
    buyer_name: str = Form(...),
    buyer_phone: str = Form(...),
    bank_tx_id: str = Form(...),
    receipt: UploadFile = File(...)
):
    receipt_filename = f"{bank_tx_id}_{receipt.filename}"
    file_path = os.path.join(UPLOAD_DIR, receipt_filename)
    
    with open(file_path, "wb") as f:
        f.write(await receipt.read())

    if engine:
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO transactions (order_id, buyer_name, buyer_phone, bank_tx_id, receipt_image)
                    VALUES (:order_id, :name, :phone, :tx_id, :img)
                """), {
                    "order_id": order_id, "name": buyer_name, "phone": buyer_phone,
                    "tx_id": bank_tx_id, "img": f"/static/uploads/{receipt_filename}"
                })
                conn.commit()
        except Exception as e:
            print(f"Payment submission error: {e}")

    return RedirectResponse(url="/?payment=success", status_code=303)
