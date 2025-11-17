from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Admin, Pegawai

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# === GET: Halaman login ===
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


# === POST: Proses login ===
@router.post("/login")
async def login_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # 🔹 Cek di tabel Admin
    admin = db.query(Admin).filter(Admin.email == email, Admin.password == password).first()
    if admin:
        return RedirectResponse(url="/admin/dashboard", status_code=302)

    # 🔹 Cek di tabel Pegawai
    pegawai = db.query(Pegawai).filter(Pegawai.email == email, Pegawai.password == password).first()
    if pegawai:
        return RedirectResponse(url=f"/pegawai/dashboard/{pegawai.id_pegawai}", status_code=302)

    # 🔹 Jika gagal login
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Email atau password salah"}
    )
