import os
from pathlib import Path

import pytest

from dat_backend.templates.python_script import build_cmr_query_url, \
    build_version_query_params, cmr_download, cmr_search, get_login_credentials, \
    get_password, get_speed, get_token, get_username, main, output_progress


@pytest.mark.parametrize(
    'version',
    ['3', '03', '003']
)
def test_build_version_query_params(version):
    actual = build_version_query_params(version)
    expected = '&version=003&version=03&version=3'
    assert actual == expected


def test_build_version_query_params_with_long_version_quits():
    with pytest.raises(SystemExit):
        build_version_query_params('3333')


parameters = [
    ('', '', '', ''),
    ('-20,-30,20,30', '', '', '&bounding_box=-20,-30,20,30'),
    ('', '-109,37,-102,37,-102,41,-109,41,-109,37', '',
     '&polygon=-109,37,-102,37,-102,41,-109,41,-109,37'),
    ('', '', 'A2019', '&options[producer_granule_id][pattern]=true&producer_granule_id[]=*A2019*'),
    ('', '', 'A2019,A2020', '&options[producer_granule_id][pattern]=true&'
        'producer_granule_id[]=*A2019*&producer_granule_id[]=*A2020*')
]


@pytest.mark.parametrize('bounding_box, polygon, filename_filter, extra_expect', parameters)
def test_build_cmr_query_url(bounding_box, polygon, filename_filter, extra_expect):
    actual = build_cmr_query_url('MOD10A2', '6', '2001-01-01T00:00:00Z', '2019-03-07T22:09:38Z',
                                 bounding_box, polygon,
                                 filename_filter, provider='NSIDC_CPRD')
    expected = 'https://cmr.earthdata.nasa.gov/search/granules.json?' \
        '&sort_key[]=start_date&sort_key[]=producer_granule_id' \
        '&page_size=2000&short_name=MOD10A2&version=006&version=06' \
        '&version=6&temporal[]=2001-01-01T00:00:00Z,2019-03-07T22:09:38Z' \
        + extra_expect + '&provider=NSIDC_CPRD'
    assert actual == expected


def test_get_username(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda text: 'myusername')
    actual = get_username()
    expected = 'myusername'
    assert actual == expected


def test_get_password(monkeypatch):
    monkeypatch.setattr('dat_backend.templates.python_script.getpass', lambda text: 'mypassword')
    actual = get_password()
    expected = 'mypassword'
    assert actual == expected


def test_get_token(monkeypatch):
    monkeypatch.setattr('dat_backend.templates.python_script.getpass', lambda text: 'mytoken')
    actual = get_token()
    expected = 'mytoken'
    assert actual == expected


def test_get_login_credentials_login_prompt(monkeypatch):
    # mock the netrc method so that the logic prompting for username and
    # password is tested
    def _netrc_fail():
        raise RuntimeError("No netrc.")
    monkeypatch.setattr('netrc.netrc', _netrc_fail)

    monkeypatch.setattr('builtins.input', lambda text: 'myusername')
    monkeypatch.setattr('dat_backend.templates.python_script.getpass', lambda text: 'mypassword')
    cred, token = get_login_credentials()
    expected = 'bXl1c2VybmFtZTpteXBhc3N3b3Jk'
    assert cred == expected
    assert token is None
    monkeypatch.setattr('builtins.input', lambda text: '')
    monkeypatch.setattr('dat_backend.templates.python_script.getpass', lambda text: 'mytoken')
    cred, token = get_login_credentials()
    expected = 'mytoken'
    assert cred is None
    assert token == expected


def test_cmr_search():
    actual = cmr_search('MOD10A2', '61', '2001-01-01T00:00:00Z', '2019-03-07T22:09:38Z',
                        '', '-109,37,-102,37,-102,41,-109,41,-109,37', '*A2019*')
    assert len(actual) == 72


def test_get_speed():
    assert get_speed(1, 0) == '1.0B/s'
    assert get_speed(0.001, 1000) == '1.0MB/s'
    assert get_speed(0.05, 1000000000) == '20.0GB/s'


def test_output_progress():
    output_progress(0, 100)


def test_cmr_download(tmpdir):
    # TODO: get download URL from cmr query. This example uses ECS, which is
    # going away!
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    cmr_download(['https://n5eil01u.ecs.nsidc.org/DP4/MOST/MOD10A2.061/2019.01.01/MOD10A2.A2019001.h09v04.061.2020286153245.hdf'])
    # # Call again so we exercise the "skip duplicate file" code path
    cmr_download(['https://n5eil01u.ecs.nsidc.org/DP4/MOST/MOD10A2.061/2019.01.01/MOD10A2.A2019001.h09v04.061.2020286153245.hdf'])
    assert Path("MOD10A2.A2019001.h09v04.061.2020286153245.hdf").is_file()
    os.chdir(original_cwd)

    # HTTP error 404
    with pytest.raises(SystemExit) as excinfo:
        cmr_download(['http://cmr.earthdata.nasa.gov/search/collectionsxxx'])
    assert excinfo.value.code == 1
    # URL error
    with pytest.raises(SystemExit) as excinfo:
        cmr_download(['httx://cmr.earthdata.nasa.gov/search/collections'])
    assert excinfo.value.code == 1


def test_main():
    with pytest.raises(SystemExit) as excinfo:
        main(['--help', '--force', '--quiet'])
    assert excinfo.value.code == 0
    with pytest.raises(SystemExit) as excinfo:
        main(['--foobar'])
    assert excinfo.value.code == 1
