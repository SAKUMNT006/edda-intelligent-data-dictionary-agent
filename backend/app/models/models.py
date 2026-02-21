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
