import requests

from dat_backend.templates.python_script import cmr_filter_urls

CMR_GRANULES_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"


def get_links(*, cmr_request_params: str, search_after_cursor: str | None = None):
    request_url = CMR_GRANULES_URL + f"?{cmr_request_params}"

    headers = {}
    if search_after_cursor:
        headers["CMR-Search-After"] = search_after_cursor
    response = requests.get(request_url, headers=headers)

    assert response.ok
    cursor = response.headers.get("CMR-Search-After")
    data_urls = cmr_filter_urls(response.json())

    return (data_urls, cursor)


if __name__ == "__main__":
    urls, cursor = get_links(
        cmr_request_params="provider=NSIDC_ECS&page_size=5&sort_key[]=-start_date&sort_key[]=producer_granule_id&short_name=ATL06&version=6&version=06&version=006&temporal[]=2018-10-14T00:00:00Z,2025-02-25T00:25:20Z&bounding_box=-180,-90,180,90&options[producer_granule_id][pattern]=true&producer_granule_id[]=*ATL06_2024*_0804*_006_01.h5*"
    )
    print(f"init number of results is {len(urls)}")
    while cursor:
        print(f"using cursor={cursor}")
        urls, cursor = get_links(
            cmr_request_params="provider=NSIDC_ECS&page_size=2000&sort_key[]=-start_date&sort_key[]=producer_granule_id&short_name=ATL06&version=6&version=06&version=006&temporal[]=2018-10-14T00:00:00Z,2025-02-19T20:51:37Z&bounding_box=-101.94,57.71,-90.21,61.13",
            search_after_cursor=cursor,
        )
        print(f"Number of results with cursor {len(urls)}")
