from sqlalchemy import Column, String, Integer
from app.db.database import Base

class Admin(Base):
    __tablename__ = "admin"

    id_admin = Column(String(30), primary_key=True, index=True)
    nama = Column(String(50), nullable=False)
    email = Column(String(30), unique=True, nullable=False)
    password = Column(String(30), nullable=False)


class Pegawai(Base):
    __tablename__ = "pegawai"

    id_pegawai = Column(String(30), primary_key=True, index=True)
    nama = Column(String(50), nullable=False)
    email = Column(String(30), unique=True, nullable=False)
    password = Column(String(30), nullable=False)
    jabatan = Column(String(50))
    pangkat = Column(String(50))
    NRP = Column(Integer)
