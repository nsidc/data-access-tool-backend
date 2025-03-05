"""Integration tests for the python script.

This primarily exists because the tests contained here require a valid .netrc
file with credentials for earthdata login.

TODO: consider adding EDL credentials for GHA use.
"""

import os
from pathlib import Path

import pytest

from dat_backend.templates.python_script import (  # type: ignore[attr-defined]
    cmr_download,
)


def test_cmr_download(tmpdir, monkeypatch):
    # Monkeypatch the username and password.
    monkeypatch.setattr(
        "builtins.input",
        lambda text: os.environ.get("EARTHDATA_USERNAME"),
    )
    monkeypatch.setattr(
        "dat_backend.templates.python_script.getpass",
        lambda text: os.environ.get("EARTHDATA_PASSWORD"),
    )

    # TODO: get download URL from cmr query. This example uses ECS, which is
    # going away!
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    cmr_download(
        [
            "https://n5eil01u.ecs.nsidc.org/DP4/MOST/MOD10A2.061/2019.01.01/MOD10A2.A2019001.h09v04.061.2020286153245.hdf"
        ]
    )
    # # Call again so we exercise the "skip duplicate file" code path
    cmr_download(
        [
            "https://n5eil01u.ecs.nsidc.org/DP4/MOST/MOD10A2.061/2019.01.01/MOD10A2.A2019001.h09v04.061.2020286153245.hdf"
        ]
    )
    assert Path("MOD10A2.A2019001.h09v04.061.2020286153245.hdf").is_file()
    os.chdir(original_cwd)

    # HTTP error 404
    with pytest.raises(SystemExit) as excinfo:
        cmr_download(["http://cmr.earthdata.nasa.gov/search/collectionsxxx"])
    assert excinfo.value.code == 1
    # URL error
    with pytest.raises(SystemExit) as excinfo:
        cmr_download(["httx://cmr.earthdata.nasa.gov/search/collections"])
    assert excinfo.value.code == 1
