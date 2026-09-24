import sys

from dat_backend import app

app.testing = True


def test_app():
    with app.test_client() as client:
        result = client.get("/")
        assert result.status_code == 200


def test_download_script():
    """Test 'normal' download script request: CMR search params passed."""
    with app.test_client() as client:
        result = client.post(
            "/api/downloader-script/",
            json={
                "bounding_box": "",
                "dataset_short_name": "ATL06",
                "dataset_version": "007",
                "filename_filter": "*ATL06_20231227235712_01402203_007_01.h5*",
                "polygon": "",
                "time_end": "2024-06-13T16:57:07Z",
                "time_start": "2018-10-14T00:00:00Z",
            },
        )

        assert result.status_code == 200

        # Ensure all "PLACEHOLDER" text has been properly replaced.
        assert "_PLACEHOLDER" not in result.text

        # Ensure the python version the script is tested against is present
        expected_python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        assert f"# Tested with Python {expected_python_version}" in result.text


def test_download_script_url_list():
    """Test case where url list is passed instead of CMR search params.

    TODO: this code path may no longer be used (it may have just been for the
    OIB portal, which has been decommissioned.
    """
    with app.test_client() as client:
        result = client.post(
            "/api/downloader-script/",
            json={
                "url_list": [
                    "https://fake.url.com/path/to/fake/granule_a",
                    "https://fake.url.com/path/to/fake/granule_b",
                    "https://fake.url.com/path/to/fake/granule_c",
                ],
            },
        )

        assert result.status_code == 200

        # Ensure all "PLACEHOLDER" text has been properly replaced.
        assert "_PLACEHOLDER" not in result.text


def test_status_endpoint():
    with app.test_client() as client:
        result = client.get("/api/status")
        assert result.status_code == 200
