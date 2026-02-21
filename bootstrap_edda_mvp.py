from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(".").resolve()

FILES: dict[str, str] = {}


def add(path: str, content: str) -> None:
    FILES[path] = dedent(content).lstrip("\n")


# =========================
# Root
# =========================
add(
    "README.md",
    """
    # EDDA — Elephantidae Data Dictionary Agent (MVP)

    EDDA is a software-only platform that connects to enterprise databases (MVP: PostgreSQL),
    extracts schema metadata, profiles data quality using sampling, generates business-friendly
    data dictionary docs (Markdown + JSON), and provides a chat interface for schema discovery.

    Aligned to prototype flow:
    Home → Add Data Source → Scan Setup → Schema Explorer → Table Tabs (Columns/Relationships/Quality/Docs) → Chat → History.

    ## Quick start

    ### 1) Start databases (metadata store + demo target DB)
    ```bash
    docker compose up -d
    ```

    ### 2) Run backend
    ```bash
    cd backend
    python -m venv .venv
    # mac/linux:
    source .venv/bin/activate
    # windows powershell:
    # .venv\\Scripts\\Activate.ps1
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000
    ```

    ### 3) Run frontend
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

    Open:
    - `http://localhost:3000`
    - `http://localhost:8000/health`

    ## Demo DB (ready out-of-the-box)
    This repo ships with a demo Postgres DB on port `5433` with PK/FK + some nulls.
    Use it as your target datasource:
    - db_type: postgres
    - host: localhost
    - port: 5433
    - database: demo
    - schema: public
    - username: demo
    - password: demo

    ## MVP endpoints
    - Datasources: `GET/POST /api/datasources`, `POST /api/datasources/test`
    - Scans: `POST /api/scans`, `GET /api/scans/{id}`, `GET /api/scans/recent`
    - Explorer: `GET /api/tables?scan_run_id=...`
    - Table tabs:
      - `GET /api/tables/{table_id}/columns`
      - `GET /api/tables/{table_id}/relationships`
      - `GET /api/tables/{table_id}/quality`
      - `GET /api/tables/{table_id}/docs`
      - `GET /api/tables/{table_id}/export?format=md|json`
    - Chat: `POST /api/chat`

    ## Notes (hackathon)
    - For speed, datasource passwords are stored in plaintext in the metadata DB. Replace with secrets/encryption later.
    - Scans run synchronously for demo simplicity. Swap to async worker later.
    """,
)

add(
    ".gitignore",
    """
    __pycache__/
    *.pyc
    .venv/
    .pytest_cache/
    .ruff_cache/
    *.log

    node_modules/
    .next/
    dist/

    .env
    .env.*

    .DS_Store
    .idea/
    .vscode/
    """,
)

add("LICENSE", "MIT License\n")

add(
    "Makefile",
    """
    .PHONY: up down backend frontend

    up:
    \tdocker compose up -d

    down:
    \tdocker compose down

    backend:
    \tcd backend && uvicorn app.main:app --reload --port 8000

    frontend:
    \tcd frontend && npm run dev
    """,
)

add(
    "docker-compose.yml",
    """
    services:
      # EDDA metadata store (what EDDA writes into)
      edda-meta-db:
        image: pgvector/pgvector:pg16
        container_name: edda-meta-db
        environment:
          POSTGRES_USER: edda
          POSTGRES_PASSWORD: edda
          POSTGRES_DB: edda_meta
        ports:
          - "5432:5432"
        volumes:
          - edda_meta_data:/var/lib/postgresql/data
        healthcheck:
          test: ["CMD-SHELL", "pg_isready -U edda -d edda_meta"]
          interval: 5s
          timeout: 5s
          retries: 10

      # Demo target DB (what EDDA connects to and scans)
      edda-demo-db:
        image: postgres:16
        container_name: edda-demo-db
        environment:
          POSTGRES_USER: demo
          POSTGRES_PASSWORD: demo
          POSTGRES_DB: demo
        ports:
          - "5433:5432"
        volumes:
          - ./demo/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
        healthcheck:
          test: ["CMD-SHELL", "pg_isready -U demo -d demo"]
          interval: 5s
          timeout: 5s
          retries: 10

    volumes:
      edda_meta_data:
    """,
)

add(
    "demo/init.sql",
    """
    -- Demo relational schema with PK/FK + some nulls + skew for profiling
    create table if not exists customers (
      customer_id varchar(20) primary key,
      full_name text not null,
      email text,
      phone text,
      created_at timestamp not null default now()
    );

    create table if not exists products (
      product_id varchar(20) primary key,
      category text,
      product_name text not null,
      price numeric(10,2) not null
    );

    create table if not exists orders (
      order_id varchar(20) primary key,
      customer_id varchar(20) not null references customers(customer_id),
      order_status text not null,
      order_date timestamp not null,
      delivered_date timestamp,
      total_amount numeric(10,2)
    );

    create table if not exists order_items (
      order_item_id serial primary key,
      order_id varchar(20) not null references orders(order_id),
      product_id varchar(20) not null references products(product_id),
      qty int not null,
      unit_price numeric(10,2) not null
    );

    create table if not exists payments (
      payment_id serial primary key,
      order_id varchar(20) not null references orders(order_id),
      payment_method text,
      payment_status text not null,
      paid_amount numeric(10,2),
      paid_at timestamp
    );

    -- seed customers (with some missing email/phone)
    insert into customers(customer_id, full_name, email, phone, created_at) values
      ('C001','Asha Verma','asha@example.com','9999911111', now() - interval '90 days'),
      ('C002','Rohit Singh',null,'9999922222', now() - interval '40 days'),
      ('C003','Neha Kumar','neha@example.com',null, now() - interval '10 days'),
      ('C004','Vikram Mehta',null,null, now() - interval '5 days')
    on conflict do nothing;

    insert into products(product_id, category, product_name, price) values
      ('P001','electronics','Wireless Mouse',599.00),
      ('P002','electronics','Keyboard',1299.00),
      ('P003','home','Water Bottle',299.00),
      ('P004','home','Desk Lamp',899.00)
    on conflict do nothing;

    insert into orders(order_id, customer_id, order_status, order_date, delivered_date, total_amount) values
      ('O1001','C001','DELIVERED', now() - interval '60 days', now() - interval '57 days', 1898.00),
      ('O1002','C002','SHIPPED',   now() - interval '12 days', null,  599.00),
      ('O1003','C003','PLACED',    now() - interval '2 days',  null,  299.00),
      ('O1004','C004','CANCELLED', now() - interval '20 days', null,  null)
    on conflict do nothing;

    insert into order_items(order_id, product_id, qty, unit_price) values
      ('O1001','P001',1,599.00),
      ('O1001','P002',1,1299.00),
      ('O1002','P001',1,599.00),
      ('O1003','P003',1,299.00)
    on conflict do nothing;

    insert into payments(order_id, payment_method, payment_status, paid_amount, paid_at) values
      ('O1001','CARD','PAID',1898.00, now() - interval '60 days'),
      ('O1002','UPI','PENDING',null, null),
      ('O1003','COD','PENDING',null, null)
    on conflict do nothing;

    create index if not exists idx_orders_customer on orders(customer_id);
    create index if not exists idx_payments_order on payments(order_id);
    """,
)

add(
    ".github/workflows/ci.yml",
    """
    name: CI
    on:
      push:
        branches: ["main","dev"]
      pull_request:
        branches: ["main","dev"]

    jobs:
      backend:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-python@v5
            with:
              python-version: "3.11"
          - run: |
              cd backend
              python -m pip install --upgrade pip
              pip install -r requirements.txt
          - run: |
              cd backend
              ruff check .
          - run: |
              cd backend
              pytest -q

      frontend:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-node@v4
            with:
              node-version: "18"
          - run: |
              cd frontend
              npm ci
          - run: |
              cd frontend
              npm run build
    """,
)

# =========================
# Backend
# =========================
add(
    "backend/requirements.txt",
    """
    fastapi==0.115.0
    uvicorn[standard]==0.30.6
    pydantic==2.9.2
    pydantic-settings==2.6.1
    sqlalchemy==2.0.35
    psycopg[binary]==3.2.2
    pandas==2.2.3
    numpy==2.1.1
    ruff==0.6.9
    pytest==8.3.3
    httpx==0.27.2
    """,
)

add(
    "backend/ruff.toml",
    """
    line-length = 100
    target-version = "py311"
    """,
)

for pkg in [
    "backend/app",
    "backend/app/api",
    "backend/app/api/routes",
    "backend/app/core",
    "backend/app/db",
    "backend/app/models",
    "backend/app/services",
    "backend/app/services/adapters",
]:
    add(f"{pkg}/__init__.py", "")

add(
    "backend/app/core/config.py",
    """
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
        EDDA_META_DB_URL: str = "postgresql+psycopg://edda:edda@localhost:5432/edda_meta"
        CORS_ALLOW_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    settings = Settings()
    """,
)

add(
    "backend/app/models/base.py",
    """
    from sqlalchemy.orm import DeclarativeBase

    class Base(DeclarativeBase):
        pass
    """,
)

add(
    "backend/app/models/models.py",
    """
    from __future__ import annotations

    from datetime import datetime
    from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, JSON, UniqueConstraint
    from sqlalchemy.orm import Mapped, mapped_column, relationship
    from app.models.base import Base

    class DataSource(Base):
        __tablename__ = "data_sources"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
        db_type: Mapped[str] = mapped_column(String(50), nullable=False)  # postgres|sqlserver|snowflake
        host: Mapped[str] = mapped_column(String(200), nullable=False)
        port: Mapped[int | None] = mapped_column(Integer, nullable=True)
        database: Mapped[str] = mapped_column(String(200), nullable=False)
        schema: Mapped[str | None] = mapped_column(String(200), nullable=True)
        username: Mapped[str] = mapped_column(String(200), nullable=False)
        password: Mapped[str] = mapped_column(Text, nullable=False)  # MVP only (plaintext)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    class ScanRun(Base):
        __tablename__ = "scan_runs"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        data_source_id: Mapped[int] = mapped_column(ForeignKey("data_sources.id"), nullable=False)
        mode: Mapped[str] = mapped_column(String(20), default="quick")
        status: Mapped[str] = mapped_column(String(20), default="running")
        sample_size: Mapped[int] = mapped_column(Integer, default=500)
        schema_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
        error: Mapped[str | None] = mapped_column(Text, nullable=True)
        started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
        data_source = relationship("DataSource")

    class TableMeta(Base):
        __tablename__ = "tables"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        scan_run_id: Mapped[int] = mapped_column(ForeignKey("scan_runs.id"), nullable=False)
        schema_name: Mapped[str] = mapped_column(String(200), nullable=False)
        table_name: Mapped[str] = mapped_column(String(200), nullable=False)
        table_type: Mapped[str] = mapped_column(String(50), default="BASE TABLE")
        row_estimate: Mapped[int | None] = mapped_column(Integer, nullable=True)
        __table_args__ = (UniqueConstraint("scan_run_id","schema_name","table_name", name="uq_scan_table"),)

    class ColumnMeta(Base):
        __tablename__ = "columns"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        table_id: Mapped[int] = mapped_column(ForeignKey("tables.id"), nullable=False)
        column_name: Mapped[str] = mapped_column(String(200), nullable=False)
        data_type: Mapped[str] = mapped_column(String(200), nullable=False)
        nullable: Mapped[bool] = mapped_column(Boolean, default=True)
        default_value: Mapped[str | None] = mapped_column(Text, nullable=True)
        is_pk: Mapped[bool] = mapped_column(Boolean, default=False)
        is_fk: Mapped[bool] = mapped_column(Boolean, default=False)
        pii_risk: Mapped[str | None] = mapped_column(String(20), nullable=True)
        __table_args__ = (UniqueConstraint("table_id","column_name", name="uq_table_column"),)

    class Relationship(Base):
        __tablename__ = "relationships"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        scan_run_id: Mapped[int] = mapped_column(ForeignKey("scan_runs.id"), nullable=False)
        from_schema: Mapped[str] = mapped_column(String(200), nullable=False)
        from_table: Mapped[str] = mapped_column(String(200), nullable=False)
        from_column: Mapped[str] = mapped_column(String(200), nullable=False)
        to_schema: Mapped[str] = mapped_column(String(200), nullable=False)
        to_table: Mapped[str] = mapped_column(String(200), nullable=False)
        to_column: Mapped[str] = mapped_column(String(200), nullable=False)
        constraint_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    class TableMetrics(Base):
        __tablename__ = "table_metrics"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        table_id: Mapped[int] = mapped_column(ForeignKey("tables.id"), nullable=False, unique=True)
        metrics_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
        quality_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
        reasons: Mapped[list | None] = mapped_column(JSON, nullable=True)

    class ColumnMetrics(Base):
        __tablename__ = "column_metrics"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        column_id: Mapped[int] = mapped_column(ForeignKey("columns.id"), nullable=False, unique=True)
        metrics_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    class TableDocs(Base):
        __tablename__ = "docs"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        table_id: Mapped[int] = mapped_column(ForeignKey("tables.id"), nullable=False, unique=True)
        doc_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
        doc_markdown: Mapped[str] = mapped_column(Text, nullable=False, default="")
        generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    """,
)

add("backend/app/models/__init__.py", "from app.models.models import *  # noqa\n")

add(
    "backend/app/db/session.py",
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    from app.models.base import Base
    from app import models  # noqa: F401 (register models)

    engine = create_engine(settings.EDDA_META_DB_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def init_db() -> None:
        Base.metadata.create_all(bind=engine)

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    """,
)

add(
    "backend/app/api/schemas.py",
    """
    from pydantic import BaseModel, Field

    class DataSourceCreate(BaseModel):
        name: str
        db_type: str = Field(pattern="^(postgres|sqlserver|snowflake)$")
        host: str
        port: int | None = None
        database: str
        schema: str | None = None
        username: str
        password: str

    class DataSourceTest(DataSourceCreate):
        pass

    class ScanCreate(BaseModel):
        data_source_id: int
        mode: str = Field(default="quick", pattern="^(quick|full)$")
        sample_size: int = 500

    class ChatRequest(BaseModel):
        scan_run_id: int
        question: str
        include_sql: bool = True
    """,
)

add(
    "backend/app/services/adapter_factory.py",
    """
    from app.services.adapters.postgres import PostgresAdapter
    from app.services.adapters.sqlserver import SqlServerAdapter
    from app.services.adapters.snowflake import SnowflakeAdapter

    def build_adapter(db_type: str, cfg: dict):
        t = (db_type or "").lower()
        if t == "postgres":
            return PostgresAdapter(cfg)
        if t == "sqlserver":
            return SqlServerAdapter(cfg)
        if t == "snowflake":
            return SnowflakeAdapter(cfg)
        raise ValueError(f"Unsupported db_type: {db_type}")
    """,
)

add(
    "backend/app/services/adapters/postgres.py",
    """
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
                tables = c.execute(text(\"\"\"
                    select table_schema, table_name, table_type
                    from information_schema.tables
                    where table_schema = :schema
                    order by table_name
                \"\"\"), {"schema": schema}).mappings().all()

                cols = c.execute(text(\"\"\"
                    select table_schema, table_name, column_name, data_type, is_nullable, column_default
                    from information_schema.columns
                    where table_schema = :schema
                    order by table_name, ordinal_position
                \"\"\"), {"schema": schema}).mappings().all()

                pks = c.execute(text(\"\"\"
                    select tc.table_schema, tc.table_name, kcu.column_name
                    from information_schema.table_constraints tc
                    join information_schema.key_column_usage kcu
                      on tc.constraint_name = kcu.constraint_name
                     and tc.table_schema = kcu.table_schema
                    where tc.constraint_type = 'PRIMARY KEY'
                      and tc.table_schema = :schema
                \"\"\"), {"schema": schema}).mappings().all()
                pk_set = {(r["table_schema"], r["table_name"], r["column_name"]) for r in pks}

                rels = c.execute(text(\"\"\"
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
                \"\"\"), {"schema": schema}).mappings().all()

                uniques = c.execute(text(\"\"\"
                    select tc.table_schema, tc.table_name, kcu.column_name, tc.constraint_name
                    from information_schema.table_constraints tc
                    join information_schema.key_column_usage kcu
                      on tc.constraint_name = kcu.constraint_name
                     and tc.table_schema = kcu.table_schema
                    where tc.constraint_type = 'UNIQUE'
                      and tc.table_schema = :schema
                \"\"\"), {"schema": schema}).mappings().all()

                idx = c.execute(text(\"\"\"
                    select schemaname as table_schema, tablename as table_name, indexname, indexdef
                    from pg_indexes
                    where schemaname = :schema
                \"\"\"), {"schema": schema}).mappings().all()

                estimates = c.execute(text(\"\"\"
                    select n.nspname as table_schema, c.relname as table_name, c.reltuples::bigint as est_rows
                    from pg_class c
                    join pg_namespace n on n.oid = c.relnamespace
                    where n.nspname = :schema and c.relkind = 'r'
                \"\"\"), {"schema": schema}).mappings().all()
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
    """,
)

add(
    "backend/app/services/adapters/sqlserver.py",
    """
    class SqlServerAdapter:
        def __init__(self, cfg: dict): self.cfg = cfg
        def test_connection(self): raise NotImplementedError
        def extract_schema(self): raise NotImplementedError
        def sample_table(self, schema: str, table: str, limit: int): raise NotImplementedError
    """,
)

add(
    "backend/app/services/adapters/snowflake.py",
    """
    class SnowflakeAdapter:
        def __init__(self, cfg: dict): self.cfg = cfg
        def test_connection(self): raise NotImplementedError
        def extract_schema(self): raise NotImplementedError
        def sample_table(self, schema: str, table: str, limit: int): raise NotImplementedError
    """,
)

add(
    "backend/app/services/profiling_service.py",
    """
    import re
    import numpy as np
    import pandas as pd

    PII_HINTS = ["email","phone","mobile","dob","ssn","passport","pan","aadhar","address"]
    EMAIL_RE = re.compile(r"[^@\\s]+@[^@\\s]+\\.[^@\\s]+")

    def detect_pii_risk(col_name: str, series: pd.Series) -> str | None:
        n = (col_name or "").lower()
        if any(h in n for h in PII_HINTS):
            return "high"
        sample = series.dropna().astype(str).head(50).tolist()
        if any(EMAIL_RE.match(v) for v in sample):
            return "high"
        return "low" if len(sample) else None

    def profile_dataframe(df: pd.DataFrame) -> tuple[dict, dict]:
        table_metrics = {"row_sampled": int(len(df))}
        col_metrics = {}
        if df.empty:
            return table_metrics, col_metrics

        null_rates = []
        for col in df.columns:
            s = df[col]
            total = len(s)
            nulls = int(s.isna().sum())
            null_pct = round((nulls/total)*100, 2) if total else 0.0
            null_rates.append(null_pct)

            m = {"null_pct": null_pct}
            try:
                m["distinct_count"] = int(s.nunique(dropna=True))
            except Exception:
                m["distinct_count"] = None

            try:
                vc = s.dropna().astype(str).value_counts().head(3)
                m["top_values"] = [{"value": k, "count": int(v)} for k,v in vc.items()]
            except Exception:
                m["top_values"] = []

            if pd.api.types.is_numeric_dtype(s):
                s2 = pd.to_numeric(s, errors="coerce").dropna()
                if len(s2):
                    m.update({
                        "min": float(s2.min()),
                        "max": float(s2.max()),
                        "mean": float(s2.mean()),
                        "p50": float(np.percentile(s2, 50)),
                        "p95": float(np.percentile(s2, 95)),
                    })
            col_metrics[col] = m

        table_metrics["avg_null_pct"] = round(float(np.mean(null_rates)), 2) if null_rates else None
        return table_metrics, col_metrics

    def compute_quality_score(table_metrics: dict) -> tuple[int, list[str]]:
        reasons = []
        score = 100
        avg_null = table_metrics.get("avg_null_pct")
        if avg_null is not None:
            penalty = min(40, int(avg_null * 0.4))
            score -= penalty
            if avg_null > 10:
                reasons.append(f"High missing values: avg null {avg_null}% (sample)")
        return max(0, min(100, score)), reasons
    """,
)

add(
    "backend/app/services/docs_service.py",
    """
    def generate_doc_json(schema_name: str, table_name: str, pk_cols: list[str], fk_cols: list[str], joins: list[dict],
                          quality_score: int | None, reasons: list[str], constraints: dict) -> dict:
        return {
            "table": f"{schema_name}.{table_name}",
            "what_it_represents": f"Table `{table_name}` in schema `{schema_name}`.",
            "grain": "One row represents one record in this table.",
            "primary_keys": pk_cols,
            "foreign_keys": fk_cols,
            "constraints": constraints,
            "common_joins": joins[:8],
            "quality_score": quality_score,
            "warnings": reasons,
            "usage_recommendations": [
                "Use primary keys for stable joins.",
                "Validate null-heavy columns before relying on them in reporting.",
                "Use date filters when querying large tables."
            ],
        }

    def render_markdown(doc: dict) -> str:
        lines = [f"# {doc['table']}", "", f"**What it represents:** {doc['what_it_represents']}", "",
                 f"**Grain:** {doc['grain']}", ""]
        if doc.get("primary_keys"):
            lines += [f"**Primary key(s):** {', '.join(doc['primary_keys'])}", ""]
        if doc.get("foreign_keys"):
            lines += [f"**Foreign key column(s):** {', '.join(doc['foreign_keys'])}", ""]

        c = doc.get("constraints") or {}
        if c.get("unique"):
            lines += ["## Unique constraints"]
            for u in c["unique"]:
                cols = ", ".join(u.get("columns", []))
                lines.append(f"- {u.get('name')}: {cols}")
            lines.append("")
        if c.get("indexes"):
            lines += ["## Indexes"]
            for i in c["indexes"][:8]:
                lines.append(f"- {i.get('indexname')}")
            lines.append("")

        if doc.get("common_joins"):
            lines += ["## Common joins"]
            for j in doc["common_joins"]:
                lines.append(f"- {j['from']} → {j['to']} ({j.get('constraint_name') or 'FK'})")
            lines.append("")

        lines += ["## Data quality", f"**Quality score:** {doc.get('quality_score')}", ""]
        if doc.get("warnings"):
            lines.append("**Warnings:**")
            for w in doc["warnings"]:
                lines.append(f"- {w}")
            lines.append("")

        lines.append("## Usage recommendations")
        for r in doc.get("usage_recommendations", []):
            lines.append(f"- {r}")
        lines.append("")
        return "\\n".join(lines)
    """,
)

add(
    "backend/app/services/scan_service.py",
    """
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
    """,
)

add(
    "backend/app/services/chat_service.py",
    """
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
    """,
)

add(
    "backend/app/api/routes/datasources.py",
    """
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
    """,
)

add(
    "backend/app/api/routes/scans.py",
    """
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
    """,
)

add(
    "backend/app/api/routes/scans_recent.py",
    """
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
    """,
)

add(
    "backend/app/api/routes/tables.py",
    """
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
    """,
)

add(
    "backend/app/api/routes/chat.py",
    """
    from fastapi import APIRouter, Depends
    from sqlalchemy.orm import Session
    from app.api.schemas import ChatRequest
    from app.db.session import get_db
    from app.services.chat_service import answer_question

    router = APIRouter()

    @router.post("")
    def chat(payload: ChatRequest, db: Session = Depends(get_db)):
        return answer_question(db, scan_run_id=payload.scan_run_id, question=payload.question, include_sql=payload.include_sql)
    """,
)

add(
    "backend/app/api/router.py",
    """
    from fastapi import APIRouter
    from app.api.routes import datasources, scans, scans_recent, tables, chat

    api_router = APIRouter()
    api_router.include_router(datasources.router, prefix="/datasources", tags=["datasources"])
    api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
    api_router.include_router(scans_recent.router, prefix="/scans", tags=["scans"])
    api_router.include_router(tables.router, prefix="/tables", tags=["tables"])
    api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
    """,
)

add(
    "backend/app/main.py",
    """
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from app.core.config import settings
    from app.db.session import init_db
    from app.api.router import api_router

    def create_app() -> FastAPI:
        app = FastAPI(title="EDDA Backend", version="0.1.0")

        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ALLOW_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.on_event("startup")
        def _startup():
            init_db()

        @app.get("/health")
        def health():
            return {"status": "ok", "service": "edda-backend"}

        app.include_router(api_router, prefix="/api")
        return app

    app = create_app()
    """,
)

add(
    "backend/tests/test_quality_score.py",
    """
    from app.services.profiling_service import compute_quality_score

    def test_penalty():
        s, r = compute_quality_score({"avg_null_pct": 60})
        assert s < 100
        assert r
    """,
)

# =========================
# Frontend (Next.js app router)
# =========================
add(
    "frontend/package.json",
    """
    {
      "name": "edda-frontend",
      "private": true,
      "version": "0.1.0",
      "scripts": {
        "dev": "next dev -p 3000",
        "build": "next build",
        "start": "next start -p 3000"
      },
      "dependencies": {
        "next": "14.2.15",
        "react": "18.3.1",
        "react-dom": "18.3.1"
      },
      "devDependencies": {
        "typescript": "5.6.3",
        "@types/node": "20.16.11",
        "@types/react": "18.3.10",
        "@types/react-dom": "18.3.0"
      }
    }
    """,
)

add("frontend/next.config.js", "module.exports = { reactStrictMode: true };\n")

add(
    "frontend/tsconfig.json",
    """
    {
      "compilerOptions": {
        "target": "ES2020",
        "lib": ["dom", "dom.iterable", "esnext"],
        "strict": true,
        "noEmit": true,
        "module": "esnext",
        "moduleResolution": "bundler",
        "jsx": "preserve",
        "paths": { "@/*": ["./*"] }
      },
      "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
      "exclude": ["node_modules"]
    }
    """,
)

add("frontend/next-env.d.ts", '/// <reference types="next" />\n/// <reference types="next/image-types/global" />\n')

add(
    "frontend/lib/api.ts",
    """
    const API_BASE = process.env.NEXT_PUBLIC_EDDA_API_BASE || "http://localhost:8000/api";

    export async function apiGet(path: string) {
      const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
      if (!res.ok) throw new Error(await res.text());
      return res.json();
    }

    export async function apiPost(path: string, body: any) {
      const res = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(await res.text());
      return res.json();
    }
    """,
)

add(
    "frontend/components/Shell.tsx",
    """
    import Link from "next/link";

    const nav = [
      { href: "/", label: "Home" },
      { href: "/datasources/new", label: "Add Data Source" },
      { href: "/scans/new", label: "Start Scan" },
      { href: "/chat", label: "Chat" },
      { href: "/history", label: "History" }
    ];

    export default function Shell({ children }: { children: React.ReactNode }) {
      return (
        <div style={{ display:"flex", minHeight:"100vh", background:"#0D1117", color:"#E9EEF5" }}>
          <aside style={{ width:240, padding:16, borderRight:"1px solid #374151" }}>
            <div style={{ fontSize:22, fontWeight:800, marginBottom:6 }}>EDDA</div>
            <div style={{ fontSize:12, color:"#9EA9B6", marginBottom:16 }}>Elephantidae Data Dictionary Agent</div>
            {nav.map(n => (
              <Link key={n.href} href={n.href} style={{
                display:"block", padding:"10px 12px", marginBottom:8, borderRadius:10,
                border:"1px solid #374151", color:"#E9EEF5", textDecoration:"none"
              }}>{n.label}</Link>
            ))}
          </aside>
          <main style={{ flex:1, padding:20 }}>{children}</main>
        </div>
      );
    }
    """,
)

add(
    "frontend/app/layout.tsx",
    """
    export const metadata = { title: "EDDA", description: "Elephantidae Data Dictionary Agent" };
    export default function RootLayout({ children }: { children: React.ReactNode }) {
      return (
        <html lang="en">
          <body style={{ margin:0, fontFamily:"system-ui, -apple-system, Segoe UI, Roboto, Arial" }}>
            {children}
          </body>
        </html>
      );
    }
    """,
)

add(
    "frontend/app/page.tsx",
    """
    "use client";
    import { useEffect, useState } from "react";
    import Shell from "@/components/Shell";
    import { apiGet } from "@/lib/api";

    export default function Home() {
      const [datasources, setDatasources] = useState<any[]>([]);
      const [scans, setScans] = useState<any[]>([]);
      const [err, setErr] = useState<string | null>(null);

      useEffect(() => {
        Promise.all([apiGet("/datasources"), apiGet("/scans/recent")])
          .then(([ds, sc]) => { setDatasources(ds); setScans(sc); })
          .catch(e => setErr(String(e)));
      }, []);

      return (
        <Shell>
          <h1 style={{ fontSize:28, marginTop:0 }}>Home</h1>
          <p style={{ color:"#9EA9B6" }}>Connect a database, scan it, and generate a trusted data dictionary.</p>
          {err && <pre style={{ color:"#FBBF24" }}>{err}</pre>}

          <h2 style={{ fontSize:18 }}>Data Sources</h2>
          <div style={{ display:"grid", gridTemplateColumns:"repeat(2, minmax(0,1fr))", gap:12 }}>
            {datasources.map(d => (
              <div key={d.id} style={{ border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22" }}>
                <div style={{ fontWeight:800 }}>{d.name}</div>
                <div style={{ color:"#9EA9B6", fontSize:12 }}>{d.db_type} • {d.host}:{d.port} • {d.database}</div>
              </div>
            ))}
          </div>

          <h2 style={{ fontSize:18, marginTop:18 }}>Recent Scans</h2>
          {scans.map(s => (
            <a key={s.id} href={`/scans/${s.id}`} style={{ textDecoration:"none", color:"#E9EEF5" }}>
              <div style={{ border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22", marginBottom:10 }}>
                <div style={{ fontWeight:700 }}>Scan #{s.id} • {s.status}</div>
                <div style={{ color:"#9EA9B6", fontSize:12 }}>schema_hash: {s.schema_hash || "--"} • sample: {s.sample_size}</div>
              </div>
            </a>
          ))}
        </Shell>
      );
    }
    """,
)

add(
    "frontend/app/datasources/new/page.tsx",
    """
    "use client";
    import { useState } from "react";
    import Shell from "@/components/Shell";
    import { apiPost } from "@/lib/api";

    export default function NewDatasource() {
      const [form, setForm] = useState<any>({
        name: "demo_db",
        db_type: "postgres",
        host: "localhost",
        port: 5433,
        database: "demo",
        schema: "public",
        username: "demo",
        password: "demo"
      });
      const [msg, setMsg] = useState("");
      const [err, setErr] = useState("");

      async function testConn() {
        setErr(""); setMsg("Testing...");
        try { await apiPost("/datasources/test", form); setMsg("Connection looks good."); }
        catch (e:any) { setErr(String(e)); setMsg(""); }
      }

      async function save() {
        setErr(""); setMsg("Saving...");
        try { const r = await apiPost("/datasources", form); setMsg(`Saved datasource id=${r.id}`); }
        catch (e:any) { setErr(String(e)); setMsg(""); }
      }

      return (
        <Shell>
          <h1 style={{ fontSize:28, marginTop:0 }}>Add Data Source</h1>
          <p style={{ color:"#9EA9B6" }}>Use read-only credentials for real DBs. Demo DB works out-of-box.</p>
          {msg && <div style={{ color:"#22C55E" }}>{msg}</div>}
          {err && <pre style={{ color:"#FBBF24" }}>{err}</pre>}

          <div style={{ display:"grid", gridTemplateColumns:"repeat(2, minmax(0,1fr))", gap:10 }}>
            {Object.entries(form).map(([k,v]) => (
              <label key={k} style={{ display:"flex", flexDirection:"column", gap:6 }}>
                <span style={{ color:"#9EA9B6", fontSize:12 }}>{k}</span>
                <input value={String(v)}
                  onChange={(e)=>setForm((p:any)=>({ ...p, [k]: k==="port" ? Number(e.target.value) : e.target.value }))}
                  style={{ padding:10, borderRadius:10, border:"1px solid #374151", background:"#161B22", color:"#E9EEF5" }}
                />
              </label>
            ))}
          </div>

          <div style={{ display:"flex", gap:10, marginTop:14 }}>
            <button onClick={testConn} style={{ padding:"10px 12px", borderRadius:10, border:"1px solid #38BDF8", background:"transparent", color:"#E9EEF5" }}>
              Test Connection
            </button>
            <button onClick={save} style={{ padding:"10px 12px", borderRadius:10, border:"1px solid #22C55E", background:"transparent", color:"#E9EEF5" }}>
              Save
            </button>
          </div>
        </Shell>
      );
    }
    """,
)

add(
    "frontend/app/scans/new/page.tsx",
    """
    "use client";
    import { useEffect, useState } from "react";
    import Shell from "@/components/Shell";
    import { apiGet, apiPost } from "@/lib/api";

    export default function StartScan() {
      const [datasources, setDatasources] = useState<any[]>([]);
      const [dataSourceId, setDataSourceId] = useState<number>(0);
      const [sampleSize, setSampleSize] = useState<number>(500);
      const [err, setErr] = useState("");

      useEffect(() => {
        apiGet("/datasources").then((ds)=> {
          setDatasources(ds);
          if (ds.length) setDataSourceId(ds[0].id);
        }).catch((e)=>setErr(String(e)));
      }, []);

      async function start() {
        setErr("");
        try {
          const r = await apiPost("/scans", { data_source_id: dataSourceId, mode: "quick", sample_size: sampleSize });
          window.location.href = `/scans/${r.scan_run_id}`;
        } catch (e:any) {
          setErr(String(e));
        }
      }

      return (
        <Shell>
          <h1 style={{ fontSize:28, marginTop:0 }}>Scan Setup</h1>
          <p style={{ color:"#9EA9B6" }}>Pick datasource + sample size. MVP runs synchronously.</p>
          {err && <pre style={{ color:"#FBBF24" }}>{err}</pre>}

          <div style={{ display:"flex", gap:12, alignItems:"center" }}>
            <label>
              <div style={{ color:"#9EA9B6", fontSize:12 }}>Datasource</div>
              <select value={dataSourceId} onChange={(e)=>setDataSourceId(Number(e.target.value))}
                style={{ padding:10, borderRadius:10, border:"1px solid #374151", background:"#161B22", color:"#E9EEF5" }}>
                {datasources.map((d)=> <option key={d.id} value={d.id}>{d.name}</option>)}
              </select>
            </label>

            <label>
              <div style={{ color:"#9EA9B6", fontSize:12 }}>Sample size / table</div>
              <input value={sampleSize} onChange={(e)=>setSampleSize(Number(e.target.value))}
                style={{ padding:10, borderRadius:10, border:"1px solid #374151", background:"#161B22", color:"#E9EEF5", width:160 }} />
            </label>

            <button onClick={start} style={{ marginTop:18, padding:"10px 12px", borderRadius:10, border:"1px solid #22C55E", background:"transparent", color:"#E9EEF5" }}>
              Start Scan
            </button>
          </div>
        </Shell>
      );
    }
    """,
)

add(
    "frontend/app/scans/[scanId]/page.tsx",
    """
    "use client";
    import { useEffect, useState } from "react";
    import Shell from "@/components/Shell";
    import { apiGet } from "@/lib/api";

    export default function ScanExplorer({ params }: { params: { scanId: string } }) {
      const scanId = Number(params.scanId);
      const [scan, setScan] = useState<any>(null);
      const [tables, setTables] = useState<any[]>([]);
      const [err, setErr] = useState("");

      useEffect(() => {
        Promise.all([apiGet(`/scans/${scanId}`), apiGet(`/tables?scan_run_id=${scanId}`)])
          .then(([s, t]) => { setScan(s); setTables(t); })
          .catch((e)=>setErr(String(e)));
      }, [scanId]);

      return (
        <Shell>
          <h1 style={{ fontSize:28, marginTop:0 }}>Schema Explorer</h1>
          {err && <pre style={{ color:"#FBBF24" }}>{err}</pre>}

          {scan && (
            <div style={{ border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22", marginBottom:12 }}>
              <div style={{ fontWeight:800 }}>Scan #{scan.id} • {scan.status}</div>
              <div style={{ color:"#9EA9B6", fontSize:12 }}>schema_hash: {scan.schema_hash || "--"} • sample: {scan.sample_size}</div>
            </div>
          )}

          <div style={{ display:"grid", gridTemplateColumns:"repeat(2, minmax(0,1fr))", gap:10 }}>
            {tables.map((t)=> (
              <a key={t.id} href={`/tables/${t.id}`} style={{ textDecoration:"none", color:"#E9EEF5" }}>
                <div style={{ border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22" }}>
                  <div style={{ fontWeight:700 }}>{t.schema_name}.{t.table_name}</div>
                  <div style={{ color:"#9EA9B6", fontSize:12 }}>row_estimate: {t.row_estimate ?? "--"}</div>
                </div>
              </a>
            ))}
          </div>
        </Shell>
      );
    }
    """,
)

add(
    "frontend/app/tables/[tableId]/page.tsx",
    """
    "use client";
    import { useEffect, useState } from "react";
    import Shell from "@/components/Shell";
    import { apiGet } from "@/lib/api";

    type Tab = "columns" | "relationships" | "quality" | "docs";

    export default function TablePage({ params }: { params: { tableId: string } }) {
      const tableId = Number(params.tableId);
      const [tab, setTab] = useState<Tab>("columns");
      const [table, setTable] = useState<any>(null);
      const [cols, setCols] = useState<any[]>([]);
      const [rels, setRels] = useState<any[]>([]);
      const [quality, setQuality] = useState<any>(null);
      const [docs, setDocs] = useState<any>(null);
      const [err, setErr] = useState("");

      useEffect(() => {
        apiGet(`/tables/${tableId}`).then(setTable).catch((e)=>setErr(String(e)));
      }, [tableId]);

      useEffect(() => {
        setErr("");
        if (tab === "columns") apiGet(`/tables/${tableId}/columns`).then(setCols).catch((e)=>setErr(String(e)));
        if (tab === "relationships") apiGet(`/tables/${tableId}/relationships`).then(setRels).catch((e)=>setErr(String(e)));
        if (tab === "quality") apiGet(`/tables/${tableId}/quality`).then(setQuality).catch((e)=>setErr(String(e)));
        if (tab === "docs") apiGet(`/tables/${tableId}/docs`).then(setDocs).catch((e)=>setErr(String(e)));
      }, [tab, tableId]);

      return (
        <Shell>
          <h1 style={{ fontSize:28, marginTop:0 }}>Table</h1>
          {err && <pre style={{ color:"#FBBF24" }}>{err}</pre>}

          {table && (
            <div style={{ border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22" }}>
              <div style={{ fontWeight:800 }}>{table.schema_name}.{table.table_name}</div>
              <div style={{ color:"#9EA9B6", fontSize:12 }}>row_estimate: {table.row_estimate ?? "--"}</div>
            </div>
          )}

          <div style={{ display:"flex", gap:10, marginTop:12 }}>
            {(["columns","relationships","quality","docs"] as Tab[]).map((t)=> (
              <button key={t} onClick={()=>setTab(t)} style={{
                padding:"8px 10px", borderRadius:10,
                border:`1px solid ${tab===t ? "#38BDF8" : "#374151"}`,
                background:"transparent", color:"#E9EEF5"
              }}>{t}</button>
            ))}
          </div>

          {tab==="columns" && (
            <div style={{ marginTop:12, border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22" }}>
              <h3 style={{ marginTop:0 }}>Columns</h3>
              <table style={{ width:"100%", borderCollapse:"collapse" }}>
                <thead>
                  <tr style={{ color:"#9EA9B6", fontSize:12, textAlign:"left" }}>
                    <th>Name</th><th>Type</th><th>Nullable</th><th>PK</th><th>FK</th><th>PII</th>
                  </tr>
                </thead>
                <tbody>
                  {cols.map(c => (
                    <tr key={c.id} style={{ borderTop:"1px solid #30363d" }}>
                      <td style={{ padding:"8px 0" }}>{c.column_name}</td>
                      <td>{c.data_type}</td>
                      <td>{String(c.nullable)}</td>
                      <td>{c.is_pk ? "PK" : ""}</td>
                      <td>{c.is_fk ? "FK" : ""}</td>
                      <td>{c.pii_risk || ""}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {tab==="relationships" && (
            <div style={{ marginTop:12, border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22" }}>
              <h3 style={{ marginTop:0 }}>Relationships</h3>
              <ul>
                {rels.map((r, i)=> (
                  <li key={i} style={{ marginBottom:8 }}>
                    {r.from} → {r.to} {r.constraint_name ? `(${r.constraint_name})` : ""}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {tab==="quality" && quality && (
            <div style={{ marginTop:12, border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22" }}>
              <h3 style={{ marginTop:0 }}>Quality</h3>
              <div>Quality score: <b>{quality.quality_score ?? "--"}</b></div>
              {quality.reasons?.length ? (
                <>
                  <div style={{ marginTop:8, color:"#9EA9B6" }}>Warnings:</div>
                  <ul>{quality.reasons.map((x:string, i:number)=> <li key={i}>{x}</li>)}</ul>
                </>
              ) : null}
              <pre style={{ marginTop:12, whiteSpace:"pre-wrap" }}>{JSON.stringify(quality.table_metrics, null, 2)}</pre>
            </div>
          )}

          {tab==="docs" && docs && (
            <div style={{ marginTop:12, border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22" }}>
              <h3 style={{ marginTop:0 }}>Docs (Markdown)</h3>
              <pre style={{ whiteSpace:"pre-wrap" }}>{docs.doc_markdown}</pre>
            </div>
          )}
        </Shell>
      );
    }
    """,
)

add(
    "frontend/app/chat/page.tsx",
    """
    "use client";
    import { useState } from "react";
    import Shell from "@/components/Shell";
    import { apiPost } from "@/lib/api";

    export default function Chat() {
      const [scanRunId, setScanRunId] = useState<number>(1);
      const [q, setQ] = useState("How do I join orders to payments?");
      const [out, setOut] = useState<any>(null);
      const [err, setErr] = useState("");

      async function ask() {
        setErr("");
        try {
          const r = await apiPost("/chat", { scan_run_id: scanRunId, question: q, include_sql: true });
          setOut(r);
        } catch (e:any) {
          setErr(String(e));
        }
      }

      return (
        <Shell>
          <h1 style={{ fontSize:28, marginTop:0 }}>Chat</h1>
          <p style={{ color:"#9EA9B6" }}>Ask schema questions grounded in stored docs/relationships.</p>

          <div style={{ display:"flex", gap:10, alignItems:"center" }}>
            <label>
              <div style={{ color:"#9EA9B6", fontSize:12 }}>scan_run_id</div>
              <input value={scanRunId} onChange={(e)=>setScanRunId(Number(e.target.value))}
                style={{ padding:10, borderRadius:10, border:"1px solid #374151", background:"#161B22", color:"#E9EEF5", width:160 }} />
            </label>
            <button onClick={ask} style={{ marginTop:18, padding:"10px 12px", borderRadius:10, border:"1px solid #38BDF8", background:"transparent", color:"#E9EEF5" }}>
              Send
            </button>
          </div>

          <textarea value={q} onChange={(e)=>setQ(e.target.value)} rows={3}
            style={{ width:"100%", padding:10, borderRadius:10, border:"1px solid #374151", background:"#161B22", color:"#E9EEF5", marginTop:10 }} />

          {err && <pre style={{ color:"#FBBF24" }}>{err}</pre>}
          {out && <pre style={{ marginTop:12, padding:12, borderRadius:12, border:"1px solid #374151", background:"#161B22" }}>{JSON.stringify(out, null, 2)}</pre>}
        </Shell>
      );
    }
    """,
)

add(
    "frontend/app/history/page.tsx",
    """
    "use client";
    import { useEffect, useState } from "react";
    import Shell from "@/components/Shell";
    import { apiGet } from "@/lib/api";

    export default function History() {
      const [scans, setScans] = useState<any[]>([]);
      const [err, setErr] = useState("");

      useEffect(() => {
        apiGet("/scans/recent").then(setScans).catch((e)=>setErr(String(e)));
      }, []);

      return (
        <Shell>
          <h1 style={{ fontSize:28, marginTop:0 }}>History</h1>
          <p style={{ color:"#9EA9B6" }}>Scan history (schema diff is a stretch feature).</p>
          {err && <pre style={{ color:"#FBBF24" }}>{err}</pre>}

          {scans.map(s => (
            <div key={s.id} style={{ border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22", marginBottom:10 }}>
              <div style={{ fontWeight:700 }}>Scan #{s.id} • {s.status}</div>
              <div style={{ color:"#9EA9B6", fontSize:12 }}>schema_hash: {s.schema_hash || "--"} • started: {s.started_at}</div>
            </div>
          ))}
        </Shell>
      );
    }
    """,
)

# =========================
# Writer
# =========================
def write_all() -> None:
    for rel, content in FILES.items():
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    # ensure python packages exist
    for pkg in [
        "backend/app",
        "backend/app/api",
        "backend/app/api/routes",
        "backend/app/core",
        "backend/app/db",
        "backend/app/models",
        "backend/app/services",
        "backend/app/services/adapters",
    ]:
        initp = ROOT / pkg / "__init__.py"
        if not initp.exists():
            initp.write_text("", encoding="utf-8")


if __name__ == "__main__":
    write_all()
    print(f"✅ EDDA MVP generated ({len(FILES)} files).")
    print("Next:")
    print("  docker compose up -d")
    print("  cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000")
    print("  cd frontend && npm install && npm run dev")