from dat_backend.app import app


app.testing = True


def test_app():
    with app.test_client() as client:
        result = client.get("/")
        assert result.status_code == 200


def test_download_script():
    with app.test_client() as client:
        result = client.post(
            "/api/downloader-script/",
            json={
                "bounding_box": "",
                "dataset_short_name": "ATL06",
                "dataset_version": "006",
                "filename_filter": "*ATL06_20231227235712_01402203_006_01.h5*",
                "polygon": "",
                "time_end": "2024-06-13T16:57:07Z",
                "time_start": "2018-10-14T00:00:00Z",
            },
        )

        assert result.status_code == 200
