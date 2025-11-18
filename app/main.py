from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

# Router
from app.routes import admin, pegawai, auth
from app.routes.scan import router as scan_router

# Database
from app.db.database import Base, engine

# ===============================
#  CREATE TABLES (AUTO)
# ===============================
Base.metadata.create_all(bind=engine)

# ===============================
#  INIT FASTAPI
# ===============================
app = FastAPI(
    title="Sistem Login, CRUD Pegawai & Network/Web Scanner",
    description="Aplikasi manajemen pegawai + scanner jaringan & website real-time",
    version="1.0"
)

# ===============================
#  REGISTER ROUTERS
# ===============================

# Auth Routes
app.include_router(
    auth.router,
    tags=["Auth"]
)

# Admin Routes
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"]
)

# Pegawai Routes
app.include_router(
    pegawai.router,
    prefix="/pegawai",
    tags=["Pegawai"]
)

# Scan Routes
app.include_router(
    scan_router,
    prefix="/scan",    # penting! jangan hapus
    tags=["Scan"]
)

# ===============================
#  ROOT REDIRECT
# ===============================
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/login")

# ===============================
#  GLOBAL LOGOUT
# ===============================
@app.get("/logout", include_in_schema=False)
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response
