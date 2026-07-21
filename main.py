import os
from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="منصة محاصيل السودان")

# إعداد Supabase
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# إعداد القوالب والملفات الثابتة
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    # جلب الأسعار من Supabase
    response = supabase.table("market_posts").select("*").order("created_at", desc=True).execute()
    posts = response.data if response.data else []
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "posts": posts}
    )


@app.get("/add-price", response_class=HTMLResponse)
async def add_price_page(request: Request):
    return templates.TemplateResponse("add_price.html", {"request": request})


@app.post("/add-price")
async def handle_add_price(
    state: str = Form(...),
    locality: str = Form(...),
    market_name: str = Form(...),
    merchant_name: str = Form(...),
    phone: str = Form(...),
    notes: str = Form(""),
    crop_names: list[str] = Form(...),
    crop_prices: list[str] = Form(...)
):
    # تجميع الأصناف والأسعار في قائمة JSON
    items = []
    for name, price in zip(crop_names, crop_prices):
        if name.strip() and price.strip():
            items.append({"name": name.strip(), "price": price.strip()})

    # تجهيز السجل للحفظ في Supabase
    new_post = {
        "state": state,
        "locality": locality,
        "market_name": market_name,
        "merchant_name": merchant_name,
        "phone": phone,
        "notes": notes,
        "items": items
    }

    supabase.table("market_posts").insert(new_post).execute()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
