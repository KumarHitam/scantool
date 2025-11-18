from sqlalchemy.orm import Session
from app.models.models import ScanHistory


# ===================================================
# CREATE SCAN HISTORY
# ===================================================
def create_scan_history(
    db: Session,
    url: str,
    status_code: int = None,
    latency_ms: int = None,
    content_length: int = None,
    dns: str = None,
    error: str = None,
    source: str = None,
):
    rec = ScanHistory(
        url=url,
        status_code=status_code,
        latency_ms=latency_ms,
        content_length=content_length,
        dns=dns,
        error=error,
        source=source
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


# ===================================================
# LIST SCAN HISTORY
# ===================================================
def list_scan_history(db: Session, limit: int = 100):
    return (
        db.query(ScanHistory)
        .order_by(ScanHistory.id.desc())
        .limit(limit)
        .all()
    )
