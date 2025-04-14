from pathlib import Path

from dat_backend.routes import metrics
from dat_backend import app


app.testing = True


TEST_METRICS_PATH = Path(__file__).parent / "test_server_logs"


def test_metrics_from_logs():
    metrics_dict = metrics.metrics_from_logs(TEST_METRICS_PATH)

    assert metrics_dict.get("max_datetime") is not None
    assert metrics_dict.get("min_datetime") is not None

    assert metrics_dict.get("total_num_requests") == 7
    assert metrics_dict["get_links_metrics"]["ATL06_6"]["200"] == 2
    assert metrics_dict["uri_specific_metrics"]["/api/status"]["count"]["200"] == 4


def test_metrics_endpoint(monkeypatch):
    monkeypatch.setattr(metrics, "SERVER_LOGS_DIR", TEST_METRICS_PATH)
    with app.test_client() as client:
        result = client.get("/api/metrics")
        assert result.status_code == 200
        assert "Total number of requests handled: 7" in result.text
