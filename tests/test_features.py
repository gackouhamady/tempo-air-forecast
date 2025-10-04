from src.pipelines.features import build_features

def test_build_features_runs():
    target = build_features()
    assert target in ("no2", "pm25", None)
