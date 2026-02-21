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
    return "\n".join(lines)
