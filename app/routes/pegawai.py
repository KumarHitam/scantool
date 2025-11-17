from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Pegawai
from app.schemas.schemas import PegawaiCreate, PegawaiOut

router = APIRouter(tags=["Pegawai"])

templates = Jinja2Templates(directory="app/templates")


# ==========================================================
# ROUTE HALAMAN (HARUS DI ATAS ROUTE DINAMIS)
# ==========================================================

# Dashboard Pegawai
@router.get("/dashboard/{id_pegawai}", response_class=HTMLResponse)
def pegawai_dashboard(id_pegawai: str, request: Request, db: Session = Depends(get_db)):
    pegawai = db.query(Pegawai).filter(Pegawai.id_pegawai == id_pegawai).first()
    if not pegawai:
        raise HTTPException(status_code=404, detail="Pegawai tidak ditemukan")

    return templates.TemplateResponse(
        "pegawai_dashboard.html",
        {"request": request, "pegawai": pegawai}
    )


# Halaman Profil
@router.get("/profil/{id_pegawai}", response_class=HTMLResponse)
def profil_pegawai(id_pegawai: str, request: Request, db: Session = Depends(get_db)):
    pegawai = db.query(Pegawai).filter(Pegawai.id_pegawai == id_pegawai).first()
    if not pegawai:
        raise HTTPException(status_code=404, detail="Pegawai tidak ditemukan")

    return templates.TemplateResponse(
        "pegawai_profil.html",
        {"request": request, "pegawai": pegawai}
    )


# Form Edit Pegawai
@router.get("/edit/{id_pegawai}", response_class=HTMLResponse)
def edit_pegawai_form(id_pegawai: str, request: Request, db: Session = Depends(get_db)):
    pegawai = db.query(Pegawai).filter(Pegawai.id_pegawai == id_pegawai).first()
    if not pegawai:
        raise HTTPException(status_code=404, detail="Pegawai tidak ditemukan")

    return templates.TemplateResponse(
        "edit_pegawai.html",
        {"request": request, "pegawai": pegawai}
    )


# Submit Edit Pegawai
@router.post("/edit/{id_pegawai}")
async def edit_pegawai_submit(id_pegawai: str, request: Request, db: Session = Depends(get_db)):
    form = await request.form()

    pegawai = db.query(Pegawai).filter(Pegawai.id_pegawai == id_pegawai).first()
    if not pegawai:
        raise HTTPException(status_code=404, detail="Pegawai tidak ditemukan")

    pegawai.nama = form.get("nama")
    pegawai.email = form.get("email")
    pegawai.jabatan = form.get("jabatan")
    pegawai.pangkat = form.get("pangkat")

    db.commit()
    db.refresh(pegawai)

    return RedirectResponse(
        url=f"/pegawai/dashboard/{id_pegawai}",
        status_code=302
    )


# Logout
@router.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response


# Halaman Home Pegawai
@router.get("/home", response_class=HTMLResponse)
def pegawai_home():
    html = """
    <html>
        <head>
            <title>Halaman Pegawai</title>
        </head>
        <body>
            <h1>Selamat Datang di Halaman Pegawai 👨‍💼</h1>
            <p>Anda berhasil login sebagai Pegawai.</p>
            <a href="/">Kembali</a>
        </body>
    </html>
    """
    return HTMLResponse(html)


# ==========================================================
# API CRUD PEGAWAI (JSON)
# ==========================================================

@router.post("/", response_model=PegawaiOut)
def create_pegawai(data: PegawaiCreate, db: Session = Depends(get_db)):
    existing = db.query(Pegawai).filter(Pegawai.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email sudah digunakan")

    new_pg = Pegawai(**data.dict())
    db.add(new_pg)
    db.commit()
    db.refresh(new_pg)
    return new_pg


@router.get("/", response_model=list[PegawaiOut])
def get_all_pegawai(db: Session = Depends(get_db)):
    return db.query(Pegawai).all()


# ==========================================================
# ROUTE DINAMIS (PALING BAWAH)
# ==========================================================

@router.get("/detail/{id_pegawai}", response_model=PegawaiOut)
def get_pegawai_by_id(id_pegawai: str, db: Session = Depends(get_db)):
    pg = db.query(Pegawai).filter(Pegawai.id_pegawai == id_pegawai).first()
    if not pg:
        raise HTTPException(status_code=404, detail="Pegawai tidak ditemukan")
    return pg


@router.put("/{id_pegawai}", response_model=PegawaiOut)
def update_pegawai(id_pegawai: str, data: PegawaiCreate, db: Session = Depends(get_db)):
    pg = db.query(Pegawai).filter(Pegawai.id_pegawai == id_pegawai).first()
    if not pg:
        raise HTTPException(status_code=404, detail="Pegawai tidak ditemukan")

    for key, value in data.dict().items():
        setattr(pg, key, value)

    db.commit()
    db.refresh(pg)
    return pg


@router.delete("/{id_pegawai}")
def delete_pegawai(id_pegawai: str, db: Session = Depends(get_db)):
    pg = db.query(Pegawai).filter(Pegawai.id_pegawai == id_pegawai).first()
    if not pg:
        raise HTTPException(status_code=404, detail="Pegawai tidak ditemukan")

    db.delete(pg)
    db.commit()
    return {"message": "Pegawai berhasil dihapus"}
