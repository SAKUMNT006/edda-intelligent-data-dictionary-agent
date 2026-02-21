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
