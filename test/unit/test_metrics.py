from io import StringIO
from pathlib import Path

import pandas as pd

from dat_backend import app
from dat_backend.routes import metrics

app.testing = True


TEST_METRICS_PATH = Path(__file__).parent / "test_server_logs"


def test_metrics_from_logs():
    metrics_df = metrics.metrics_from_logs(TEST_METRICS_PATH)

    assert metrics_df.index.name == "datetime"
    assert "short_name" in metrics_df
    assert "dataset_version" in metrics_df

    assert len(metrics_df[metrics_df["short_name"] == "ATL06"]) == 2


def test_metrics_endpoint(monkeypatch):
    monkeypatch.setattr(metrics, "SERVER_LOGS_DIR", TEST_METRICS_PATH)
    with app.test_client() as client:
        result = client.get("/api/metrics")
        assert result.status_code == 200
        csv_data = StringIO(result.text)
        df_from_csv = pd.read_csv(csv_data)
        assert len(df_from_csv[df_from_csv["short_name"] == "ATL06"]) == 2
