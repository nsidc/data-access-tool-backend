import datetime as dt
import gzip
import io
import json
import re
from pathlib import Path
from urllib.parse import parse_qs

import flask_restx as frx
import pandas as pd
from flask import send_file
from werkzeug.wrappers import Response

from dat_backend import api, cache
from dat_backend.constants import RESPONSE_CODES

SERVER_LOGS_DIR = Path("/tmp/server_logs/")


def _get_links_metrics(access_info: dict[str, str]) -> dict[str, str | None] | None:

    if "get-links" not in access_info["uri"]:
        return None

    datetime_str = access_info["time_iso8601"]

    request_params_dict = parse_qs(access_info["args"])
    # Indicates that a new get-links request has been initiated.
    if "cursor" not in request_params_dict.keys():
        # missing cmr request params - request was not formatted correctly.
        if "cmr_request_params" not in request_params_dict:
            return None
        cmr_request_params = parse_qs(request_params_dict["cmr_request_params"][0])
        # missing short name - request was not formatted correctly.
        if (
            "short_name" not in cmr_request_params
            or "version" not in cmr_request_params
        ):
            return None

        dataset_short_name = cmr_request_params["short_name"][0]
        dataset_version = cmr_request_params["version"][0]

        return {
            "short_name": dataset_short_name,
            "dataset_version": dataset_version,
            "datetime": datetime_str,
        }

    return None


_http_referer_pattern = re.compile(
    r"https://nsidc.org/data/data-access-tool/(?P<dataset_shortname>.*)/versions/(?P<dataset_version>[^?]*)"
)


def _get_python_script_metrics(
    access_info: dict[str, str],
) -> dict[str, str | None] | None:
    if "downloader-script" not in access_info["uri"]:
        return None

    datetime_str = access_info["time_iso8601"]

    # NOTE: we can infer the dataset name and version from the `http_referrer`,
    # but we can't get the params from the request dict because this was sent as
    # a POST payload and that's not included in the logs.
    dataset_shortname = None
    dataset_version = None
    match = _http_referer_pattern.match(access_info["http_referer"])
    if match:
        dataset_shortname = match.group("dataset_shortname")
        dataset_version = match.group("dataset_version")

    return {
        "short_name": dataset_shortname,
        "dataset_version": dataset_version,
        "datetime": datetime_str,
    }


def metrics_from_logs(server_logs_dir: Path) -> pd.DataFrame:
    metrics_list: list[dict[str, str | None]] = []

    logfiles = list(server_logs_dir.rglob("dat.access.log*"))
    for logfile in logfiles:
        open_func = open
        if logfile.suffix == ".gz":
            open_func = gzip.open  # type: ignore[assignment]
        with open_func(logfile, "rb") as logfile:  # type: ignore[assignment]
            for line in logfile:  # type: ignore[attr-defined]
                try:
                    # Try to decode the line explicitly here (instead of using
                    # `open_func(logfile, "rt")` because some log lines are
                    # corrupted with invalid start bytes.
                    # According to Claude, these lines are likely "TLS packets"
                    # that are being sent ia http and can be safely
                    # ignored. Requests look like e.g.,
                    # `\\u0016\\u0003\\u0001\\u0002\\u0000\\u0001\\u0000\\u0001\xfc\\u0003\\u0003`.
                    decoded_line = line.decode("utf8")
                    access_info = json.loads(decoded_line)
                except Exception:
                    continue

                # Filter for only the successful requests
                if access_info["status"] != "200":
                    continue

                metrics_info = None
                if metrics_info := _get_links_metrics(access_info):
                    metrics_info["handoff_type"] = "get-links"
                elif metrics_info := _get_python_script_metrics(access_info):
                    metrics_info["handoff_type"] = "python-script"

                if metrics_info:
                    metrics_list.append(metrics_info)

    df = pd.DataFrame(metrics_list)

    df = df.set_index("datetime").sort_index()

    return df


@api.route("/api/metrics")
class ApplicationMetrics(frx.Resource):  # type: ignore[misc]
    # Implement a 2.5 minute cache for metrics
    @cache.cached(timeout=150)
    @api.response(*RESPONSE_CODES[200])  # type: ignore[untyped-decorator]
    @api.response(*RESPONSE_CODES[500])  # type: ignore[untyped-decorator]
    def get(self) -> Response:
        metrics_df = metrics_from_logs(SERVER_LOGS_DIR)

        output = io.BytesIO()
        metrics_df.to_csv(
            output,
            index=True,
            encoding="utf-8",
        )
        output.seek(0)

        return send_file(
            output,
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"DAT_handoff_metrics_{dt.datetime.now().isoformat()}.csv",
        )
