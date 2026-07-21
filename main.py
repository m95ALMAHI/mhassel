import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client

# تحميل ملف .env للمحيط المحلي
load_dotenv()

# قراءة وتنظيف متغيرات البيئة تلقائياً لمنع أخطاء Invalid URL / Invalid Key
SUPABASE_URL = (os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL") or "").strip()
SUPABASE_KEY = (os.getenv("SUPABASE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or "").strip()

# طباعة للتأكد في سجلات Render (Logs)
print(f"--> Initializing Supabase with URL: '{SUPABASE_URL}'")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("⚠️ Error: SUPABASE_URL or SUPABASE_KEY environment variable is missing!")

# إنشاء عميل الاتصال بـ Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# إنشاء تطبيق FastAPI
app = FastAPI(title="محاصيل السودان - Mahaseel Sudan")

# ربط المجلدات الثابتة والقوالب
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ----------------------------------------------------
# المسارات (Routes)
# ----------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    الصفحة الرئيسية: عرض أسعار المحاصيل الحالية
    """
    try:
        # جلب البيانات من جدول الاسعار في Supabase
        response = supabase.table("prices").select("*").order("created_at", desc=True).execute()
        prices = response.data if response.data else []
    except Exception as e:
        print(f"Error fetching prices: {e}")
        prices = []

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "prices": prices}
    )


@app.get("/add-price", response_class=HTMLResponse)
async def add_price_page(request: Request):
    """
    صفحة إضافة سعر جديد لمادة أو محصول
    """
    return templates.TemplateResponse("add_price.html", {"request": request})


@app.post("/add-price")
async def add_price_submit(
    crop_name: str = Form(...),
    market_location: str = Form(...),
    price: float = Form(...),
    unit: str = Form(...)
):
    """
    استلام بيانات السعر الجديد وحفظها في Supabase
    """
    try:
        new_entry = {
            "crop_name": crop_name,
            "market_location": market_location,
            "price": price,
            "unit": unit
        }
        supabase.table("prices").insert(new_entry).execute()
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        print(f"Error inserting price: {e}")
        return RedirectResponse(url="/add-price?error=1", status_code=303)


@app.get("/health")
async def health_check():
    """
    مسار للفحص الدائم لسيرفر Render (Health Check)
    """
    return {"status": "healthy", "project": "Mahaseel Sudan"}
