import datetime as dt
import gzip
import json
from pathlib import Path
from collections import defaultdict
from urllib.parse import parse_qs
from typing import Any

import flask_restx as frx
from flask import render_template
from werkzeug.wrappers import Response

from dat_backend import api, cache
from dat_backend.constants import RESPONSE_CODES


SERVER_LOGS_DIR = Path("/tmp/server_logs/")


def _request_ip_from_log(log_line: dict[str, str]) -> str:
    ips = log_line["x_forwarded_for"]
    # There may be multiple IPs depending on how many proxy hops were
    # involved. Sitting behind the NSIDC apache proxy, this would usually be
    # 2. The first would be the originator's IP, and the second is the proxy's
    # IP.
    first_ip = ips.split(",")[0]

    return first_ip


def metrics_from_logs(server_logs_dir: Path) -> dict[str, Any]:
    total_num_requests = 0
    uri_specific_metrics: dict[str, dict[Any, Any]] = defaultdict(dict)
    get_links_metrics: dict[str, dict[Any, Any]] = defaultdict(dict)
    min_datetime = None
    max_datetime = None

    logfiles = server_logs_dir.rglob("dat.access.log*")
    for logfile in logfiles:
        open_func = open
        if logfile.suffix == ".gz":
            open_func = gzip.open  # type: ignore[assignment]
        with open_func(logfile, "rt") as logfile:  # type: ignore[assignment]
            for line in logfile:  # type: ignore[attr-defined]
                try:
                    access_info = json.loads(line)
                except Exception:
                    continue

                # skip swagger endpoints. The `/` response should be enough to
                # give us an idea of how many requests are being made to API
                # docs.
                if "swagger" in access_info["uri"]:
                    continue
                # Skip reporting metrics on favicon
                if "favicon" in access_info["uri"]:
                    continue

                if min_datetime is None or min_datetime > access_info["time_iso8601"]:
                    min_datetime = access_info["time_iso8601"]
                if max_datetime is None or max_datetime < access_info["time_iso8601"]:
                    max_datetime = access_info["time_iso8601"]

                total_num_requests += 1
                if "count" in uri_specific_metrics[access_info["uri"]].keys():
                    uri_specific_metrics[access_info["uri"]]["count"][
                        access_info["status"]
                    ] += 1
                    uri_specific_metrics[access_info["uri"]]["ips"].add(
                        _request_ip_from_log(access_info)
                    )
                else:
                    uri_specific_metrics[access_info["uri"]]["count"] = defaultdict(
                        lambda: 1
                    )
                    uri_specific_metrics[access_info["uri"]]["count"][
                        access_info["status"]
                    ] = 1
                    uri_specific_metrics[access_info["uri"]]["ips"] = set(
                        [
                            _request_ip_from_log(access_info),
                        ]
                    )

                if "get-links" in access_info["uri"]:
                    request_params_dict = parse_qs(access_info["args"])
                    # Indicates that a new get-links request has been initiated.
                    if "cursor" not in request_params_dict.keys():
                        cmr_request_params = parse_qs(
                            request_params_dict["cmr_request_params"][0]
                        )
                        shortname_version = (
                            cmr_request_params["short_name"][0]
                            + "_"
                            + cmr_request_params["version"][0]
                        )
                        if shortname_version in get_links_metrics.keys():
                            get_links_metrics[shortname_version][
                                access_info["status"]
                            ] += 1
                        else:
                            get_links_metrics[shortname_version] = defaultdict(
                                lambda: 1
                            )
                            get_links_metrics[shortname_version][
                                access_info["status"]
                            ] = 1

    return {
        "uri_specific_metrics": uri_specific_metrics,
        "get_links_metrics": get_links_metrics,
        "total_num_requests": total_num_requests,
        "max_datetime": max_datetime,
        "min_datetime": min_datetime,
    }


@api.route("/api/metrics")
class ApplicationMetrics(frx.Resource):  # type: ignore[misc]
    # Implement a 2.5 minute cache for metrics
    @cache.cached(timeout=150)
    @api.response(*RESPONSE_CODES[200])  # type: ignore[misc]
    @api.response(*RESPONSE_CODES[500])  # type: ignore[misc]
    def get(self) -> Response:
        metrics = metrics_from_logs(SERVER_LOGS_DIR)
        total_num_requests = metrics["total_num_requests"]
        metrics_by_uri = metrics["uri_specific_metrics"]
        get_links_metrics = metrics["get_links_metrics"]
        return Response(
            render_template(
                "app_metrics.html.jinja",
                request_time=dt.datetime.now(),
                max_datetime=metrics["max_datetime"],
                min_datetime=metrics["min_datetime"],
                total_num_requests=total_num_requests,
                metrics_by_uri=metrics_by_uri,
                get_links_metrics=get_links_metrics,
            ),
            content_type="text/html",
        )
