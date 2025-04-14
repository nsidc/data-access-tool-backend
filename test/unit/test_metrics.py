from pathlib import Path

from dat_backend.routes.metrics import metrics_from_logs


def test_metrics_from_logs():
    test_metrics_path = Path(__file__).parent / "test_server_logs"
    metrics = metrics_from_logs(test_metrics_path)

    assert metrics.get("max_datetime") is not None
    assert metrics.get("min_datetime") is not None

    assert metrics.get("total_num_requests") == 7
    assert metrics["get_links_metrics"]["ATL06_6"]["200"] == 2
    assert metrics["uri_specific_metrics"]["/api/status"]["count"]["200"] == 4
