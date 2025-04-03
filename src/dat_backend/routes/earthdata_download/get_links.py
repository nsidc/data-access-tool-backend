import requests
import flask_restx as frx
from flask import (
    request,
)

from dat_backend import api, app
from dat_backend.constants import RESPONSE_CODES
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


get_links_response_model = api.model(
    "GetLinksResponse",
    {
        "links": frx.fields.List(
            frx.fields.String(
                example="https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL06/006/2024/02/09/ATL06_20240209110944_08042201_006_01.h5"
            )
        ),
        "done": frx.fields.Boolean(example=False),
        "cursor": frx.fields.String(
            example='[1638327816913,"atl06_20211201030329_10641303_006_01.h5",2706594203]'
        ),
    },
)


@api.route("/api/get-links")
class GetLinks(frx.Resource):  # type: ignore[misc]

    @api.marshal_with(get_links_response_model, mask=False)
    @api.response(*RESPONSE_CODES[200])
    @api.response(*RESPONSE_CODES[500])
    @api.param(
        "cmr_request_params",
        description="CMR Request parameters as a string",
        example=r"provider=NSIDC_CPRD&page_size=5&sort_key[]=-start_date&sort_key[]=producer_granule_id&short_name=ATL06&version=6&version=06&version=006&temporal[]=2018-10-14T00:00:00Z,2025-02-25T00:25:20Z&bounding_box=-180,-90,180,90&options[producer_granule_id][pattern]=true&producer_granule_id[]=\*ATL06_2024\*_0804\*_006_01.h5\*",
        required=True,
    )
    @api.param(
        "cursor",
        description="CMR search results cursor",
        example='[1638327816913,"atl06_20211201030329_10641303_006_01.h5",2706594203]',
        required=False,
    )
    def get(self):
        cmr_request_params = request.args["cmr_request_params"]
        cursor = request.args.get("cursor")
        app.logger.info(
            f"get_links received successfully: {cmr_request_params=} {cursor=}"
        )

        app.logger.info(f"get_links using {cursor=}")
        links, cursor = get_links(
            cmr_request_params=cmr_request_params,
            search_after_cursor=cursor,
        )
        app.logger.info(f"get_links found new {cursor=}")

        orders_done = len(links) == 0
        if not orders_done:
            app.logger.info(f"first link: {links[0]}")
        response = {
            "links": links,
            "done": orders_done,
            "cursor": cursor,
        }

        return response
