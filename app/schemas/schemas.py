from pydantic import BaseModel

# ======= ADMIN =======

class AdminBase(BaseModel):
    id_admin: str
    nama: str
    email: str
    password: str

class AdminOut(AdminBase):
    class Config:
        orm_mode = True


# ======= PEGAWAI =======

class PegawaiBase(BaseModel):
    id_pegawai: str
    nama: str
    email: str
    password: str
    jabatan: str | None = None
    pangkat: str | None = None
    NRP: int | None = None

class PegawaiCreate(PegawaiBase):
    pass

class PegawaiOut(PegawaiBase):
    class Config:
        orm_mode = True
