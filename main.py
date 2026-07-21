import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client

load_dotenv()

# تنظيف المتغيرات من أي مسافات فارغة أو أسطر جديدة قد تحدث عند النسخ
SUPABASE_URL = (os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL") or "").strip()
SUPABASE_KEY = (os.getenv("SUPABASE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or "").strip()

# طباعة لتأكيد القراءة في سجلات Render
print(f"--> [DEBUG] SUPABASE_URL: '{SUPABASE_URL}' (Length: {len(SUPABASE_URL)})")

if not SUPABASE_URL:
    raise ValueError("❌ SUPABASE_URL is missing or empty!")
if not SUPABASE_KEY:
    raise ValueError("❌ SUPABASE_KEY is missing or empty!")

# إنشاء عميل Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Mahaseel Sudan")

# ربط الملفات الثابتة والقوالب
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        response = supabase.table("prices").select("*").order("created_at", desc=True).execute()
        prices = response.data if response.data else []
    except Exception as e:
        print(f"Error fetching prices: {e}")
        prices = []

    return templates.TemplateResponse("index.html", {"request": request, "prices": prices})

@app.get("/health")
async def health_check():
    return {"status": "ok"}
