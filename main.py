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

# تحميل متغيرات البيئة (.env)
load_dotenv()

# إعداد اتصال قاعدة البيانات Supabase / PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None

app = FastAPI(title="بورصة محاصيل السودان")

# مجلد المرفقات لحفظ صور إشعارات بنكك / التحويلات
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# نظام حماية لوحة المدير (Basic Auth)
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

# ---------------------------------------------------------
# 1️⃣ الصفحة الرئيسية (عرض بورصة الأسعار والتداولات)
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    orders = []
    if engine:
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM market_orders ORDER BY created_at DESC"))
                raw_orders = [dict(row._mapping) for row in result]
                
                # إنشاء رابط الواتساب المباشر لكل عرض
                for order in raw_orders:
                    msg = f"السلام عليكم، أرغب في الاستفسار/طلب محصول: {order['crop_name']}\nالكمية: {order['quantity']}\nالسعر: {order['price_per_unit']} SDG\nالمنطقة: {order['state']}"
                    order['wa_link'] = f"https://wa.me/{order['phone']}?text={urllib.parse.quote(msg)}"
                    orders.append(order)
        except Exception as e:
            print(f"Error fetching market orders: {e}")

    return templates.TemplateResponse("index.html", {"request": request, "orders": orders})

# ---------------------------------------------------------
# 2️⃣ لوحة تحكم المدير (إضافة نشرة أسعار جديدة)
# ---------------------------------------------------------
@app.get("/admin", response_class=HTMLResponse)
@app.get("/add-price", response_class=HTMLResponse)
async def admin_dashboard(request: Request, username: str = Depends(authenticate_admin)):
    transactions = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT * FROM transactions ORDER BY created_at DESC"))
                transactions = [dict(row._mapping) for row in res]
        except Exception as e:
            print(f"Admin fetch error: {e}")

    return templates.TemplateResponse("admin.html", {"request": request, "transactions": transactions})

# مسار معالجة إضافة النشرة من قبل المدير
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
            print(f"Error adding price: {e}")

    return RedirectResponse(url="/", status_code=303)

# ---------------------------------------------------------
# 3️⃣ إضافة عرض أو طلب جديد من المستخدمين
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 4️⃣ تسجيل وتأكيد إشعار الدفع البنكي
# ---------------------------------------------------------
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
