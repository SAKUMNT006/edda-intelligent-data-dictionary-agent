from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import ScanRun

router = APIRouter()

@router.get("/recent")
def recent_scans(db: Session = Depends(get_db)):
    rows = db.query(ScanRun).order_by(ScanRun.started_at.desc()).limit(10).all()
    return [{
        "id": r.id,
        "data_source_id": r.data_source_id,
        "status": r.status,
        "sample_size": r.sample_size,
        "schema_hash": r.schema_hash,
        "started_at": r.started_at.isoformat(),
        "finished_at": r.finished_at.isoformat() if r.finished_at else None,
    } for r in rows]
