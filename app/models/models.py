from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

# ==========================================
# MODEL ADMIN
# ==========================================
class Admin(Base):
    __tablename__ = "admin"

    id_admin = Column(String(30), primary_key=True, index=True)
    nama = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)     # ← lebih aman


# ==========================================
# MODEL PEGAWAI
# ==========================================
class Pegawai(Base):
    __tablename__ = "pegawai"

    id_pegawai = Column(String(30), primary_key=True, index=True)
    nama = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)     # ← sama
    jabatan = Column(String(50), nullable=True)
    pangkat = Column(String(50), nullable=True)
    NRP = Column(Integer, nullable=True)


# ==========================================
# MODEL SCAN HISTORY
# ==========================================
class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(512), nullable=False)
    status_code = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    content_length = Column(Integer, nullable=True)
    dns = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    source = Column(String(50), nullable=True)  # web, agent, bulk
    created_at = Column(DateTime(timezone=True), server_default=func.now())
