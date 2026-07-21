import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client

load_dotenv()

# قراءة وتنظيف القيم
SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").strip()
SUPABASE_KEY = (os.getenv("SUPABASE_KEY") or "").strip()

# تهيئة العميل بأسلوب محمي تجنباً لـ Crash السيرفر
supabase: Client = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("--> [SUCCESS] Supabase connected successfully!")
    except Exception as e:
        print(f"--> [ERROR] Supabase initialization failed: {e}")
else:
    print(f"--> [WARNING] Environment variables missing. URL: '{SUPABASE_URL}', Key Length: {len(SUPABASE_KEY)}")

app = FastAPI(title="Mahaseel Sudan")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    prices = []
    if supabase:
        try:
            res = supabase.table("prices").select("*").order("created_at", desc=True).execute()
            prices = res.data or []
        except Exception as e:
            print(f"Database query error: {e}")

    return templates.TemplateResponse("index.html", {"request": request, "prices": prices})

# مسار جديد للتحقق من البيئة مباشرة من المتصفح
@app.get("/debug-env")
async def debug_env():
    return {
        "supabase_url_value": SUPABASE_URL,
        "supabase_url_is_valid": SUPABASE_URL.startswith("https://"),
        "supabase_key_length": len(SUPABASE_KEY),
        "is_connected": supabase is not None
    }
