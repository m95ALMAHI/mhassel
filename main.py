import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, text
from fastapi import Form
from fastapi.responses import RedirectResponse

load_dotenv()

# قراءة سلسلة اتصال ببيانات Supabase عبر PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# إصلاح البادئة في حال كانت تبدأ بـ postgres:// بدلاً من postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# إنشاء المحرك (Engine) للاتصال بقاعدة البيانات
engine = None
if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        print("--> [SUCCESS] Connected to PostgreSQL successfully!")
    except Exception as e:
        print(f"--> [ERROR] Failed to connect to database: {e}")

app = FastAPI(title="Mahaseel Sudan")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    prices = []
    if engine:
        try:
            with engine.connect() as connection:
                result = connection.execute(text("SELECT * FROM prices ORDER BY created_at DESC"))
                # تحويل النتائج إلى القواميس (Dicts) لتمريرها للقالب
                prices = [dict(row._mapping) for row in result]
        except Exception as e:
            print(f"Error fetching prices: {e}")

    return templates.TemplateResponse("index.html", {"request": request, "prices": prices})

@app.get("/health")
async def health_check():
    return {"status": "ok", "db_connected": engine is not None}

# 1. مسار عرض صفحة إضافة نشرة جديدة
@app.get("/add-price", response_class=HTMLResponse)
async def show_add_form(request: Request):
    return templates.TemplateResponse("add_price.html", {"request": request})


# 2. مسار معالجة وحفظ البيانات في PostgreSQL
@app.post("/add-price")
async def add_price(
    crop_name: str = Form(...),
    price: float = Form(...),
    state: str = Form(...)
):
    if engine:
        try:
            with engine.connect() as connection:
                # استبدل أسماء الأعمدة بما يطابق جدولك في Supabase
                query = text("""
                    INSERT INTO prices (crop_name, price, state) 
                    VALUES (:crop_name, :price, :state)
                """)
                connection.execute(query, {
                    "crop_name": crop_name, 
                    "price": price, 
                    "state": state
                })
                connection.commit()
        except Exception as e:
            print(f"Error inserting data: {e}")

    # إعادة التوجيه للصفحة الرئيسية بعد الإضافة
    return RedirectResponse(url="/", status_code=303)
