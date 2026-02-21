from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import TableMeta, ColumnMeta, Relationship, TableMetrics, ColumnMetrics, TableDocs

router = APIRouter()

@router.get("")
def list_tables(scan_run_id: int = Query(...), db: Session = Depends(get_db)):
    tables = db.query(TableMeta).filter(TableMeta.scan_run_id == scan_run_id).order_by(TableMeta.table_name.asc()).all()
    return [{"id": t.id, "schema_name": t.schema_name, "table_name": t.table_name, "row_estimate": t.row_estimate} for t in tables]

@router.get("/{table_id}")
def get_table(table_id: int, db: Session = Depends(get_db)):
    t = db.query(TableMeta).filter(TableMeta.id == table_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Table not found")
    return {"id": t.id, "scan_run_id": t.scan_run_id, "schema_name": t.schema_name, "table_name": t.table_name, "row_estimate": t.row_estimate}

@router.get("/{table_id}/columns")
def get_columns(table_id: int, db: Session = Depends(get_db)):
    cols = db.query(ColumnMeta).filter(ColumnMeta.table_id == table_id).order_by(ColumnMeta.column_name.asc()).all()
    return [{"id": c.id, "column_name": c.column_name, "data_type": c.data_type, "nullable": c.nullable,
             "default_value": c.default_value, "is_pk": c.is_pk, "is_fk": c.is_fk, "pii_risk": c.pii_risk} for c in cols]

@router.get("/{table_id}/relationships")
def get_relationships(table_id: int, db: Session = Depends(get_db)):
    t = db.query(TableMeta).filter(TableMeta.id == table_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Table not found")
    rels = db.query(Relationship).filter(Relationship.scan_run_id == t.scan_run_id).all()
    out = []
    for r in rels:
        if (r.from_schema == t.schema_name and r.from_table == t.table_name) or (r.to_schema == t.schema_name and r.to_table == t.table_name):
            out.append({"from": f"{r.from_schema}.{r.from_table}.{r.from_column}",
                        "to": f"{r.to_schema}.{r.to_table}.{r.to_column}",
                        "constraint_name": r.constraint_name})
    return out

@router.get("/{table_id}/quality")
def get_quality(table_id: int, db: Session = Depends(get_db)):
    tm = db.query(TableMetrics).filter(TableMetrics.table_id == table_id).first()
    if not tm:
        return {"quality_score": None, "reasons": [], "table_metrics": {}, "column_metrics": []}
    cols = db.query(ColumnMeta).filter(ColumnMeta.table_id == table_id).all()
    cm_out = []
    for c in cols:
        cm = db.query(ColumnMetrics).filter(ColumnMetrics.column_id == c.id).first()
        if cm:
            cm_out.append({"column_name": c.column_name, "metrics": cm.metrics_json})
    return {"quality_score": tm.quality_score, "reasons": tm.reasons or [], "table_metrics": tm.metrics_json, "column_metrics": cm_out}

@router.get("/{table_id}/docs")
def get_docs(table_id: int, db: Session = Depends(get_db)):
    doc = db.query(TableDocs).filter(TableDocs.table_id == table_id).first()
    if not doc:
        return {"doc_json": {}, "doc_markdown": ""}
    return {"doc_json": doc.doc_json, "doc_markdown": doc.doc_markdown}

@router.get("/{table_id}/export")
def export_docs(table_id: int, format: str = Query("md", pattern="^(md|json)$"), db: Session = Depends(get_db)):
    doc = db.query(TableDocs).filter(TableDocs.table_id == table_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Docs not found")
    return {"format": format, "content": doc.doc_markdown if format == "md" else doc.doc_json}
