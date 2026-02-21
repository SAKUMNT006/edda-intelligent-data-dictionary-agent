class SqlServerAdapter:
    def __init__(self, cfg: dict): self.cfg = cfg
    def test_connection(self): raise NotImplementedError
    def extract_schema(self): raise NotImplementedError
    def sample_table(self, schema: str, table: str, limit: int): raise NotImplementedError
