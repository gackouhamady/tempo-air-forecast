from src.pipelines.ingest import fetch_openmeteo

def test_openmeteo_fetch_ok():
    df = fetch_openmeteo(48.8566, 2.3522, 1)
    assert df is not None
    assert df.shape[0] > 0
