from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Ganti sesuai user, password, dan nama database MySQL kamu
DATABASE_URL = "mysql+mysqlconnector://root:@localhost/scan_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DATABASE_URL = "mysql+mysqlconnector://root:@localhost/scan_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ✅ Tambahkan fungsi ini
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
