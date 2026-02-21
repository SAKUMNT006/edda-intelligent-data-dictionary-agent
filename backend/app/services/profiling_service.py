import re
import numpy as np
import pandas as pd

PII_HINTS = ["email","phone","mobile","dob","ssn","passport","pan","aadhar","address"]
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")

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
