from app.services.profiling_service import compute_quality_score

def test_penalty():
    s, r = compute_quality_score({"avg_null_pct": 60})
    assert s < 100
    assert r
