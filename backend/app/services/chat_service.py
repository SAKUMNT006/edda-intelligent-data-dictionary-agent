import re
from sqlalchemy.orm import Session
from app.models.models import ScanRun, TableMeta, TableDocs, Relationship, ColumnMeta

def answer_question(db: Session, scan_run_id: int, question: str, include_sql: bool):
    scan = db.query(ScanRun).filter(ScanRun.id == scan_run_id).first()
    if not scan:
        return {"answer": "Invalid scan_run_id", "referenced_objects": [], "sql_suggestion": None, "sources": []}

    q = (question or "").lower()
    tables = db.query(TableMeta).filter(TableMeta.scan_run_id == scan_run_id).all()
    rels = db.query(Relationship).filter(Relationship.scan_run_id == scan_run_id).all()

    if re.search(r"join|relationship|connect", q) and rels:
        mentioned = [t.table_name for t in tables if t.table_name.lower() in q]
        picked = None
        if len(mentioned) >= 2:
            a, b = mentioned[0], mentioned[1]
            for r in rels:
                if (r.from_table == a and r.to_table == b) or (r.from_table == b and r.to_table == a):
                    picked = r; break
        if not picked:
            picked = rels[0]

        sql = None
        if include_sql:
            sql = f"SELECT * FROM {picked.from_table} a JOIN {picked.to_table} b ON a.{picked.from_column}=b.{picked.to_column} LIMIT 100;"
        return {
            "answer": f"A common join is {picked.from_table}.{picked.from_column} → {picked.to_table}.{picked.to_column}.",
            "referenced_objects": [f"{picked.from_table}.{picked.from_column}", f"{picked.to_table}.{picked.to_column}"],
            "sql_suggestion": sql,
            "sources": ["relationships"],
        }

    for t in tables:
        if t.table_name.lower() in q:
            doc = db.query(TableDocs).filter(TableDocs.table_id == t.id).first()
            if doc and doc.doc_markdown:
                return {
                    "answer": doc.doc_markdown[:1200],
                    "referenced_objects": [f"{t.schema_name}.{t.table_name}"],
                    "sql_suggestion": None,
                    "sources": ["docs"],
                }

    cols = (
        db.query(ColumnMeta)
        .join(TableMeta, ColumnMeta.table_id == TableMeta.id)
        .filter(TableMeta.scan_run_id == scan_run_id)
        .all()
    )
    hits = [c.column_name for c in cols if c.column_name.lower() in q]
    if hits:
        return {
            "answer": f"Matching columns: {', '.join(sorted(set(hits)))}",
            "referenced_objects": sorted(set(hits))[:10],
            "sql_suggestion": None,
            "sources": ["schema"],
        }

    return {
        "answer": "Try: 'What does orders represent?' or 'How do I join orders to payments?'",
        "referenced_objects": [],
        "sql_suggestion": None,
        "sources": [],
    }
