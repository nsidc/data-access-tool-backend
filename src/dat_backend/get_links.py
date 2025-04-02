import requests

from dat_backend.templates.python_script import cmr_filter_urls  # type: ignore[attr-defined]

CMR_GRANULES_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"


def get_links(
    *,
    cmr_request_params: str,
    search_after_cursor: str | None = None,
) -> tuple[list[str], str | None]:
    request_url = CMR_GRANULES_URL + f"?{cmr_request_params}"

    headers = {}
    if search_after_cursor:
        headers["CMR-Search-After"] = search_after_cursor
    response = requests.get(request_url, headers=headers)

    assert response.ok
    cursor = response.headers.get("CMR-Search-After")
    data_urls = cmr_filter_urls(response.json())

    return (data_urls, cursor)
