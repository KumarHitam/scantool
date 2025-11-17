from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Pegawai

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ======================
# DASHBOARD ADMIN
# ======================
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    jumlah_pegawai = db.query(Pegawai).count()
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "jumlah_pegawai": jumlah_pegawai
    })


# ======================
# CRUD PEGAWAI
# ======================
@router.get("/pegawai", response_class=HTMLResponse)
def list_pegawai(request: Request, db: Session = Depends(get_db)):
    pegawai = db.query(Pegawai).all()
    return templates.TemplateResponse("pegawai_list.html", {
        "request": request,
        "pegawai": pegawai
    })


@router.post("/pegawai/tambah")
def tambah_pegawai(
    nama: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    jabatan: str = Form(...),
    pangkat: str = Form(...),
    NRP: int = Form(...),
    db: Session = Depends(get_db)
):
    id_baru = f"P{len(db.query(Pegawai).all()) + 1:03}"
    pegawai = Pegawai(
        id_pegawai=id_baru,
        nama=nama,
        email=email,
        password=password,
        jabatan=jabatan,
        pangkat=pangkat,
        NRP=NRP
    )
    db.add(pegawai)
    db.commit()
    return RedirectResponse(url="/admin/pegawai", status_code=302)


@router.post("/pegawai/hapus")
def hapus_pegawai(id_pegawai: str = Form(...), db: Session = Depends(get_db)):
    pegawai = db.query(Pegawai).filter(Pegawai.id_pegawai == id_pegawai).first()
    if pegawai:
        db.delete(pegawai)
        db.commit()
    return RedirectResponse(url="/admin/pegawai", status_code=302)
# ======================
# EDIT PEGAWAI
# ======================
@router.get("/pegawai/edit/{id_pegawai}", response_class=HTMLResponse)
def form_edit_pegawai(request: Request, id_pegawai: str, db: Session = Depends(get_db)):
    pegawai = db.query(Pegawai).filter(Pegawai.id_pegawai == id_pegawai).first()
    if not pegawai:
        return RedirectResponse(url="/admin/pegawai", status_code=302)
    return templates.TemplateResponse("edit_pegawai.html", {
        "request": request,
        "pegawai": pegawai
    })


@router.post("/pegawai/edit/{id_pegawai}")
def update_pegawai(
    id_pegawai: str,
    nama: str = Form(...),
    email: str = Form(...),
    jabatan: str = Form(...),
    pangkat: str = Form(...),
    db: Session = Depends(get_db)
):
    pegawai = db.query(Pegawai).filter(Pegawai.id_pegawai == id_pegawai).first()
    if pegawai:
        pegawai.nama = nama
        pegawai.email = email
        pegawai.jabatan = jabatan
        pegawai.pangkat = pangkat
        db.commit()
    return RedirectResponse(url="/admin/pegawai", status_code=302)
