from urllib.parse import quote

from dat_backend.app import app


app.testing = True


def _get_links_response(cursor: str | None = None):
    with app.test_client() as client:
        # This request results in 31 granule results.
        cmr_request_params = "provider=NSIDC_CPRD&page_size=5&sort_key[]=-start_date&sort_key[]=producer_granule_id&short_name=ATL06&version=6&version=06&version=006&temporal[]=2018-10-14T00:00:00Z,2025-02-25T00:25:20Z&bounding_box=-180,-90,180,90&options[producer_granule_id][pattern]=true&producer_granule_id[]=*ATL06_2024*_0804*_006_01.h5*"
        url_encoded_cmr_request_params = quote(cmr_request_params)
        cursor_query_param = ""
        if cursor:
            cursor_query_param = f"&cursor={cursor}"
        result = client.get(
            f"/api/get-links?cmr_request_params={url_encoded_cmr_request_params}{cursor_query_param}"
        )

        assert result.status_code == 200

    return result


def test_get_links():
    result = _get_links_response()
    assert "cursor" in result.json
    assert "links" in result.json
    assert "done" in result.json

    # Assert that we have the expected number of data links
    # TODO: this is currently driven by the `page_size` param given in the
    # cmr request params. Eventually we may want to extract this as a
    # separate query param that overrides whatever is given by the
    # cmr_query_params.
    data_links = [link for link in result.json["links"] if link.endswith(".h5")]
    assert len(data_links) == 5
    assert result.json["done"] is False

    for idx in range(1, 7 + 1):
        if result.json["done"]:
            # 31 ganules, 5 granules per page.
            raise RuntimeError(f"Expected only 7 pages of results. Done after {idx}")

        result = _get_links_response(result.json["cursor"])
        data_links.extend(
            [link for link in result.json["links"] if link.endswith(".h5")]
        )

    # The result should be done.
    assert result.json["done"]
    # Ensure that each new page provides a new set of links.
    assert len(data_links) == len(set(data_links))

    # We expect a total of 31 granule results for the query.
    assert len(data_links) == 31
