# EDDA — Elephantidae Data Dictionary Agent

EDDA is a software-only solution that connects to enterprise databases (PostgreSQL / SQL Server / Snowflake), automatically generates AI-enhanced data dictionaries, profiles data quality, produces business-friendly documentation, and provides a chat interface for natural-language schema discovery.

This repo is aligned to the Round-2 prototype screens:
Home → Add Data Source → Scan Setup → Schema Explorer → Columns → Relationships → Quality → Docs → Chat → History/Diff.

---

## Why EDDA
Database documentation is often missing or outdated. Technical metadata lacks business context, so analysts waste time guessing what fields mean, joining tables incorrectly, and trusting incomplete or stale data. EDDA makes schema, relationships, and data health visible and explains it in plain language.

---

## What EDDA does (PS11 alignment)

### 1) Connects to multiple databases
- PostgreSQL (implemented first for MVP/demo)
- SQL Server (adapter stub; planned)
- Snowflake (adapter stub; planned)

### 2) Extracts complete schema metadata
- Tables, columns, data types, nullability, defaults
- PK/FK relationships + constraint names
- (Optional) indexes / unique constraints where available

### 3) Data quality + on-the-go statistical profiling
- Completeness (null %)
- Freshness (timestamp staleness; planned/optional)
- Key health (PK null rate + uniqueness rate)
- FK health (sample orphan rate)
- Stats: top values, distinct count, min/max/mean, p50/p95 (sample-based)

### 4) AI-enhanced business documentation
- Table purpose + grain (“one row means…”)
- Common joins (derived from FK graph)
- Usage notes + warnings (grounded in measured metrics)

### 5) Documentation artifacts
- Export **Markdown** + **JSON**
- Store snapshots for history, diff, and incremental updates

### 6) Conversational chat interface
- Ask natural language questions about schema and joins
- Answers cite referenced tables/columns and can suggest **SELECT-only** SQL
