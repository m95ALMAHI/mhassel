import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client

load_dotenv()

# تنظيف القراءات
SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").strip()
SUPABASE_KEY = (os.getenv("SUPABASE_KEY") or "").strip()

print(f"--> [DEBUG] URL: '{SUPABASE_URL}' | Key Length: {len(SUPABASE_KEY)}")

supabase: Client = None

# تهيئة العميل بأمان لتجنب إيقاف السيرفر
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("--> [SUCCESS] Supabase initialized successfully!")
    except Exception as e:
        print(f"--> [ERROR] Supabase init failed: {e}")
else:
    print("--> [WARNING] SUPABASE_URL or SUPABASE_KEY is missing!")

app = FastAPI(title="Mahaseel Sudan")

# المجلدات الثابتة والقوالب
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
            print(f"Error fetching data: {e}")
            
    return templates.TemplateResponse("index.html", {"request": request, "prices": prices})

@app.get("/health")
async def health_check():
    return {"status": "ok", "supabase_connected": supabase is not None}
