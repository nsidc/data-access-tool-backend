import subprocess
import tempfile
from pathlib import Path

from dat_backend import app

app.testing = True


def test_download_script():
    """Test 'normal' download script request: CMR search params passed.

    This is a near-duplicate of the test in `unit/test_api.py`, but it actually asserts the script works as expected.
    """
    with app.test_client() as client:
        filename_filter_glob = "*ATL06_20231227235712_01402203_007_01.h5*"
        result = client.post(
            "/api/downloader-script/",
            json={
                "bounding_box": "",
                "dataset_short_name": "ATL06",
                "dataset_version": "007",
                "filename_filter": filename_filter_glob,
                "polygon": "",
                "time_end": "2024-06-13T16:57:07Z",
                "time_start": "2018-10-14T00:00:00Z",
            },
        )

        assert result.status_code == 200

        with tempfile.TemporaryDirectory() as tempdir:
            temp_dir_path = Path(tempdir)
            py_script_fp = temp_dir_path / "python_download_script.py"
            with open(py_script_fp, "w") as f:
                f.write(result.text)

            script_result = subprocess.run(
                f"python {py_script_fp}",
                shell=True,
                capture_output=True,
                text=True,
                cwd=temp_dir_path,
                check=False,
            )

            assert script_result.returncode == 0

            # Assert that the one expected h5 file was downloaded.
            assert len(list(temp_dir_path.glob("*.h5"))) == 1
            assert len(list(temp_dir_path.glob(filename_filter_glob))) == 1
