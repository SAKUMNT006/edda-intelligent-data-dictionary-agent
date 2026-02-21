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
# .venv\Scripts\Activate.ps1
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
