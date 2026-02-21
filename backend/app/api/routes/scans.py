from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.schemas import ScanCreate
from app.db.session import get_db
from app.models.models import ScanRun, DataSource
from app.services.scan_service import run_scan_sync

router = APIRouter()

@router.post("")
def start_scan(payload: ScanCreate, db: Session = Depends(get_db)):
    ds = db.query(DataSource).filter(DataSource.id == payload.data_source_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Data source not found")

    scan = ScanRun(data_source_id=ds.id, mode=payload.mode, status="running", sample_size=payload.sample_size)
    db.add(scan); db.commit(); db.refresh(scan)

    try:
        run_scan_sync(db, scan_id=scan.id)
    except Exception as e:
        scan.status = "failed"; scan.error = str(e); db.commit()
        raise

    return {"scan_run_id": scan.id}

@router.get("/{scan_id}")
def get_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(ScanRun).filter(ScanRun.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {
        "id": scan.id,
        "data_source_id": scan.data_source_id,
        "mode": scan.mode,
        "status": scan.status,
        "sample_size": scan.sample_size,
        "schema_hash": scan.schema_hash,
        "error": scan.error,
        "started_at": scan.started_at.isoformat(),
        "finished_at": scan.finished_at.isoformat() if scan.finished_at else None,
    }
