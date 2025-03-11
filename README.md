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

In dev:

```
earthdata-download://startDownload?getLinks=https://dev.hermes.trst2284.dev.int.nsidc.org/api/get-links?cmr_request_params=foo&downloadId=atl06_06&clientId=data_access_tool&authUrl=https://dev.hermes.trst2284.dev.int.nsidc.org/api/earthdata/auth?eddRedirect=earthdata-download%3A%2F%2FauthCallback
```

In integration:

```
earthdata-download://startDownload?getLinks=https://integration.nsidc.org/apps/data-access-tool/api/get-links?cmr_request_params=foo&downloadId=atl06_06&clientId=data_access_tool&authUrl=https://integration.nsidc.org/apps/data-access-tool/api/earthdata/auth?eddRedirect=earthdata-download%3A%2F%2FauthCallback
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
