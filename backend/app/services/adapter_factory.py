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
