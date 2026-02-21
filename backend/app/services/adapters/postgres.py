import hashlib
from sqlalchemy import create_engine, text

class PostgresAdapter:
    def __init__(self, cfg: dict):
        self.cfg = cfg

    def _url(self) -> str:
        host = self.cfg["host"]
        port = self.cfg.get("port") or 5432
        db = self.cfg["database"]
        user = self.cfg["username"]
        pwd = self.cfg["password"]
        return f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}"

    def test_connection(self) -> None:
        eng = create_engine(self._url(), pool_pre_ping=True)
        with eng.connect() as c:
            c.execute(text("select 1"))

    def extract_schema(self) -> dict:
        eng = create_engine(self._url(), pool_pre_ping=True)
        schema = self.cfg.get("schema") or "public"
        with eng.connect() as c:
            tables = c.execute(text("""
                select table_schema, table_name, table_type
                from information_schema.tables
                where table_schema = :schema
                order by table_name
            """), {"schema": schema}).mappings().all()

            cols = c.execute(text("""
                select table_schema, table_name, column_name, data_type, is_nullable, column_default
                from information_schema.columns
                where table_schema = :schema
                order by table_name, ordinal_position
            """), {"schema": schema}).mappings().all()

            pks = c.execute(text("""
                select tc.table_schema, tc.table_name, kcu.column_name
                from information_schema.table_constraints tc
                join information_schema.key_column_usage kcu
                  on tc.constraint_name = kcu.constraint_name
                 and tc.table_schema = kcu.table_schema
                where tc.constraint_type = 'PRIMARY KEY'
                  and tc.table_schema = :schema
            """), {"schema": schema}).mappings().all()
            pk_set = {(r["table_schema"], r["table_name"], r["column_name"]) for r in pks}

            rels = c.execute(text("""
                select
                  tc.table_schema as from_schema,
                  tc.table_name as from_table,
                  kcu.column_name as from_column,
                  ccu.table_schema as to_schema,
                  ccu.table_name as to_table,
                  ccu.column_name as to_column,
                  tc.constraint_name
                from information_schema.table_constraints tc
                join information_schema.key_column_usage kcu
                  on tc.constraint_name = kcu.constraint_name
                 and tc.table_schema = kcu.table_schema
                join information_schema.constraint_column_usage ccu
                  on ccu.constraint_name = tc.constraint_name
                 and ccu.table_schema = tc.table_schema
                where tc.constraint_type = 'FOREIGN KEY'
                  and tc.table_schema = :schema
            """), {"schema": schema}).mappings().all()

            uniques = c.execute(text("""
                select tc.table_schema, tc.table_name, kcu.column_name, tc.constraint_name
                from information_schema.table_constraints tc
                join information_schema.key_column_usage kcu
                  on tc.constraint_name = kcu.constraint_name
                 and tc.table_schema = kcu.table_schema
                where tc.constraint_type = 'UNIQUE'
                  and tc.table_schema = :schema
            """), {"schema": schema}).mappings().all()

            idx = c.execute(text("""
                select schemaname as table_schema, tablename as table_name, indexname, indexdef
                from pg_indexes
                where schemaname = :schema
            """), {"schema": schema}).mappings().all()

            estimates = c.execute(text("""
                select n.nspname as table_schema, c.relname as table_name, c.reltuples::bigint as est_rows
                from pg_class c
                join pg_namespace n on n.oid = c.relnamespace
                where n.nspname = :schema and c.relkind = 'r'
            """), {"schema": schema}).mappings().all()
            est_map = {(r["table_schema"], r["table_name"]): int(r["est_rows"]) for r in estimates}

        fp = hashlib.sha256()
        for t in tables:
            fp.update(f"T|{t['table_schema']}|{t['table_name']}|{t['table_type']}".encode())
        for ccol in cols:
            fp.update(f"C|{ccol['table_schema']}|{ccol['table_name']}|{ccol['column_name']}|{ccol['data_type']}|{ccol['is_nullable']}".encode())
        for r in rels:
            fp.update(f"R|{r['from_table']}|{r['from_column']}|{r['to_table']}|{r['to_column']}".encode())

        return {
            "schema": schema,
            "tables": [dict(t) | {"row_estimate": est_map.get((t["table_schema"], t["table_name"]))} for t in tables],
            "columns": [dict(c) | {"is_pk": (c["table_schema"], c["table_name"], c["column_name"]) in pk_set} for c in cols],
            "relationships": [dict(r) for r in rels],
            "unique_constraints": [dict(u) for u in uniques],
            "indexes": [dict(i) for i in idx],
            "schema_hash": fp.hexdigest(),
        }

    def sample_table(self, schema: str, table: str, limit: int) -> list[dict]:
        eng = create_engine(self._url(), pool_pre_ping=True)
        sql = text(f'SELECT * FROM "{schema}"."{table}" LIMIT :lim')
        with eng.connect() as c:
            rows = c.execute(sql, {"lim": limit}).mappings().all()
        return [dict(r) for r in rows]
