from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.schemas import DataSourceCreate, DataSourceTest
from app.db.session import get_db
from app.models.models import DataSource
from app.services.adapter_factory import build_adapter

router = APIRouter()

@router.get("")
def list_datasources(db: Session = Depends(get_db)):
    rows = db.query(DataSource).order_by(DataSource.created_at.desc()).all()
    return [{
        "id": r.id, "name": r.name, "db_type": r.db_type,
        "host": r.host, "port": r.port, "database": r.database,
        "schema": r.schema, "username": r.username,
        "created_at": r.created_at.isoformat()
    } for r in rows]

@router.post("")
def create_datasource(payload: DataSourceCreate, db: Session = Depends(get_db)):
    if db.query(DataSource).filter(DataSource.name == payload.name).first():
        raise HTTPException(status_code=409, detail="Data source name already exists")
    ds = DataSource(**payload.model_dump())
    db.add(ds); db.commit(); db.refresh(ds)
    return {"id": ds.id}

@router.post("/test")
def test_connection(payload: DataSourceTest):
    adapter = build_adapter(payload.db_type, payload.model_dump())
    adapter.test_connection()
    return {"ok": True}
