from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from app.routes import admin, pegawai, auth
from app.db.database import Base, engine

# Buat tabel di database jika belum ada
Base.metadata.create_all(bind=engine)

# Inisialisasi aplikasi
app = FastAPI(title="Sistem Login & CRUD Pegawai")

# ==========================================================
# REGISTER ROUTER DENGAN PREFIX AMAN
# ==========================================================

# Router Login / Register
app.include_router(auth.router, tags=["Auth"])

# Router Admin
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"]
)

# Router Pegawai
app.include_router(
    pegawai.router,
    prefix="/pegawai",
    tags=["Pegawai"]
)


# ==========================================================
# ROUTE HALAMAN UTAMA
# ==========================================================

# Arahkan root ke halaman login
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/login")


# ==========================================================
# GLOBAL LOGOUT (AMAN UNTUK SEMUA USER)
# ==========================================================

@app.get("/logout", include_in_schema=False)
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response
