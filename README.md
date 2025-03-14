# Data Access Tool (DAT) Backend

Backend services for the
[Data Access Tool UI](https://github.com/nsidc/data-access-tool-ui).

A Flask-based API provides:

- The`python_script.py` download script for data granules matching a user's
  filters.
- The
  [getLinks](https://github.com/nasa/earthdata-download/blob/main/docs/GET_LINKS.md)
  service required for DAT integration with the
  [NASA Earthdata Downloader](https://github.com/nasa/earthdata-download).

Note that this service was originally a part of the
[hermes-api](https://bitbucket.org/nsidc/hermes-api/src). It was moved to a
standalone service to support the decommissioning of ECS and the rest of the
hermes stack planned for July 2026.

## Dev

### Pre-commit

This project uses [pre-commit](https://pre-commit.com/) to run pre-commit hooks
that check and format this project's code for stylistic consistency (e.g., using
`ruff` and `black`) .

The pre-commit configuration for this project can be found in
`.pre-commit-config.yaml`. Configuration for specific tools (e.g., `vulture`) is
given in the included `pyproject.toml`.

For more information about using `pre-commit`, please sese the
[Scientific Python Library Development Guide's section on pre-commit](https://learn.scientific-python.org/development/guides/gha-basic/#pre-commit).

To install pre-commit to run checks for each commit you make:

```
$ pre-commit install
```

To manually run the pre-commit hooks without a commit:

```
$ pre-commit run --all-files
```

> [!NOTE] GitHub actions are configured to run pre-commit for all PRs and pushes
> to the `main` branch. See
> [.github/workflows/pre-commit.yml](.github/workflows/pre-commit.yml).

### Running tests

Before manually running tests, setup the `EARTHDATA_USERNAME` and
`EARTHDATA_PASSWORD` envvars, which are necessary for integration tests.

Next, to run all tests:

```
scripts/run_tests.sh
```

> [!NOTE] GitHub actions are configured to run unit tests that do not require
> Earthdata login credentials for all PRs and pushes to the `main` branch. See
> [.github/workflows/test.yml](.github/workflows/test.yml).

### Testing the EDD integration

An example deep-link to initiate EDD downloads:

In integration (note: for the get-links query param, the `cmr_request_params`
were url-encoded, and then the entire URL was url-encoded):

```
earthdata-download://startDownload?getLinks=https%3A//integration.nsidc.org/apps/data-access-tool/api/get-links%3Fcmr_request_params%3Dprovider%253DNSIDC_CPRD%2526page_size%253D5%2526sort_key%255B%255D%253D-start_date%2526sort_key%255B%255D%253Dproducer_granule_id%2526short_name%253DATL06%2526version%253D6%2526version%253D06%2526version%253D006%2526temporal%255B%255D%253D2018-10-14T00%253A00%253A00Z%252C2025-02-25T00%253A25%253A20Z%2526bounding_box%253D-180%252C-90%252C180%252C90%2526options%255Bproducer_granule_id%255D%255Bpattern%255D%253Dtrue%2526producer_granule_id%255B%255D%253D%252AATL06_2024%252A_0804%252A_006_01.h5%252A&downloadId=atl06_06&clientId=data_access_tool&authUrl=https://integration.nsidc.org/apps/data-access-tool/api/earthdata/auth?eddRedirect=earthdata-download%3A%2F%2FauthCallback
```

A button needs to be added to the Data Access Tool that will issue a GET request
that looks like the above.

The GET request to `earthdata-download://startDownload` should include the
following query parameters:

- `getLinks`: URI for `/api/get-links/`. This URI will specify the
  `cmr_request_params` query-parameter, which is a string representing the CMR
  query parameters mapping to a user's selections in the DAT.
- `downloadId`: The dataset ID and version for the current order (e.g., ATL06 v6
  is `atl06_06`)
- `authUrl`: URI for `/api/earthdata/auth/`. EDD will use this to initiate a
  token exchange with URS to authenticate user downloads. This URL must include
  `eddRedirect=earthdata-download%3A%2F%2FauthCallback` as a query parameter.

> [!WARNING] As of this writing, the CMR query parameters are hard-coded to
> always return a small subset of ATL06 v6 data.
