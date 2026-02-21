from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session

from app.models.models import (
    ScanRun, DataSource, TableMeta, ColumnMeta, Relationship,
    TableMetrics, ColumnMetrics, TableDocs
)
from app.services.adapter_factory import build_adapter
from app.services.profiling_service import profile_dataframe, compute_quality_score, detect_pii_risk
from app.services.docs_service import generate_doc_json, render_markdown

def run_scan_sync(db: Session, scan_id: int) -> None:
    scan = db.query(ScanRun).filter(ScanRun.id == scan_id).first()
    if not scan:
        raise ValueError("Scan not found")

    ds = db.query(DataSource).filter(DataSource.id == scan.data_source_id).first()
    if not ds:
        raise ValueError("Data source not found")

    adapter = build_adapter(ds.db_type, {
        "host": ds.host, "port": ds.port, "database": ds.database,
        "schema": ds.schema, "username": ds.username, "password": ds.password
    })

    schema_blob = adapter.extract_schema()
    scan.schema_hash = schema_blob.get("schema_hash")

    db.query(TableMeta).filter(TableMeta.scan_run_id == scan.id).delete()
    db.query(Relationship).filter(Relationship.scan_run_id == scan.id).delete()
    db.commit()

    table_id = {}
    for t in schema_blob["tables"]:
        tm = TableMeta(
            scan_run_id=scan.id,
            schema_name=t["table_schema"],
            table_name=t["table_name"],
            table_type=t.get("table_type") or "BASE TABLE",
            row_estimate=t.get("row_estimate"),
        )
        db.add(tm); db.flush()
        table_id[(tm.schema_name, tm.table_name)] = tm.id
    db.commit()

    for r in schema_blob.get("relationships", []):
        db.add(Relationship(
            scan_run_id=scan.id,
            from_schema=r["from_schema"],
            from_table=r["from_table"],
            from_column=r["from_column"],
            to_schema=r["to_schema"],
            to_table=r["to_table"],
            to_column=r["to_column"],
            constraint_name=r.get("constraint_name"),
        ))
    db.commit()

    fk_set = {(r["from_schema"], r["from_table"], r["from_column"]) for r in schema_blob.get("relationships", [])}
    for c in schema_blob["columns"]:
        tid = table_id.get((c["table_schema"], c["table_name"]))
        if not tid:
            continue
        db.add(ColumnMeta(
            table_id=tid,
            column_name=c["column_name"],
            data_type=c["data_type"],
            nullable=(c["is_nullable"].lower() == "yes"),
            default_value=c.get("column_default"),
            is_pk=bool(c.get("is_pk")),
            is_fk=(c["table_schema"], c["table_name"], c["column_name"]) in fk_set
        ))
    db.commit()

    uniq_by_table = {}
    for u in schema_blob.get("unique_constraints", []):
        uniq_by_table.setdefault((u["table_schema"], u["table_name"]), {}).setdefault(u.get("constraint_name"), []).append(u["column_name"])

    idx_by_table = {}
    for i in schema_blob.get("indexes", []):
        idx_by_table.setdefault((i["table_schema"], i["table_name"]), []).append(i)

    all_rels = db.query(Relationship).filter(Relationship.scan_run_id == scan.id).all()
    tables = db.query(TableMeta).filter(TableMeta.scan_run_id == scan.id).all()

    for t in tables:
        rows = adapter.sample_table(t.schema_name, t.table_name, scan.sample_size)
        df = pd.DataFrame(rows)

        t_metrics, c_metrics = profile_dataframe(df)
        score, reasons = compute_quality_score(t_metrics)

        tm = db.query(TableMetrics).filter(TableMetrics.table_id == t.id).first()
        if tm:
            tm.metrics_json = t_metrics
            tm.quality_score = score
            tm.reasons = reasons
        else:
            db.add(TableMetrics(table_id=t.id, metrics_json=t_metrics, quality_score=score, reasons=reasons))
        db.commit()

        cols = db.query(ColumnMeta).filter(ColumnMeta.table_id == t.id).all()
        col_map = {c.column_name: c for c in cols}
        for name, m in c_metrics.items():
            cobj = col_map.get(name)
            if not cobj:
                continue
            if name in df.columns:
                try:
                    cobj.pii_risk = detect_pii_risk(name, df[name])
                except Exception:
                    pass
            cm = db.query(ColumnMetrics).filter(ColumnMetrics.column_id == cobj.id).first()
            if cm:
                cm.metrics_json = m
            else:
                db.add(ColumnMetrics(column_id=cobj.id, metrics_json=m))
        db.commit()

        joins = []
        for r in all_rels:
            if (r.from_schema == t.schema_name and r.from_table == t.table_name) or (r.to_schema == t.schema_name and r.to_table == t.table_name):
                joins.append({
                    "from": f"{r.from_schema}.{r.from_table}.{r.from_column}",
                    "to": f"{r.to_schema}.{r.to_table}.{r.to_column}",
                    "constraint_name": r.constraint_name,
                })

        pk_cols = [c.column_name for c in cols if c.is_pk]
        fk_cols = [c.column_name for c in cols if c.is_fk]
        unique_list = [{"name": cname, "columns": cols_list} for cname, cols_list in (uniq_by_table.get((t.schema_name, t.table_name), {}) or {}).items()]
        constraints = {"unique": unique_list, "indexes": idx_by_table.get((t.schema_name, t.table_name), [])}

        doc_json = generate_doc_json(t.schema_name, t.table_name, pk_cols, fk_cols, joins, score, reasons, constraints)
        doc_md = render_markdown(doc_json)

        doc = db.query(TableDocs).filter(TableDocs.table_id == t.id).first()
        if doc:
            doc.doc_json = doc_json
            doc.doc_markdown = doc_md
        else:
            db.add(TableDocs(table_id=t.id, doc_json=doc_json, doc_markdown=doc_md))
        db.commit()

    scan.status = "completed"
    scan.finished_at = datetime.utcnow()
    db.commit()
