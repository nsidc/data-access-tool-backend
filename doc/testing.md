## GitHub Actions

The `data-access-tool-backend` repository is setup to utilize
[GitHub Actions](https://docs.github.com/en/actions) to automatically test the
DAT backend code in PRs and merges with the `main` branch.

See `.github/workflows/` for all configured GitHub actions for this project.

::: {.callout-warning}

Not all defined tests are run automatically through GitHub Actions. See the
sections below for details on how to ensure you are running all tests.

:::

## Pre-commit

This project uses [pre-commit](https://pre-commit.com/) to run pre-commit hooks
that check and format this project's code for stylistic consistency (e.g., using
`ruff` and `black`) .

The pre-commit configuration for this project can be found in
`.pre-commit-config.yaml`. Configuration for specific tools (e.g., `vulture`) is
given in the included `pyproject.toml`.

For more information about using `pre-commit`, please sese the
[Scientific Python Library Development Guide's section on pre-commit](https://learn.scientific-python.org/development/guides/gha-basic/#pre-commit).

To install pre-commit to run checks for each commit you make:

::: {.callout-note}

Pre-commit should already be setup for you on an
[NSIDC Data Access Tool VM](https://github.com/nsidc/data-access-tool-vm).

:::

```bash
pre-commit install
```

To manually run the pre-commit hooks without a commit:

```bash
pre-commit run --all-files
```

::: {.callout-note}

GitHub actions are configured to run pre-commit for all PRs and pushes to the
`main` branch. See `.github/workflows/pre-commit.yml`.

:::

## Running tests

Before manually running tests, setup the `EARTHDATA_USERNAME` and
`EARTHDATA_PASSWORD` envvars, which are necessary for integration tests. This
can be set to your own personal EDL credentials.

Next, to run all tests:

```
scripts/run_tests.sh
```

::: {.callout-note}

GitHub actions are configured to run unit tests that do not require Earthdata
login credentials for all PRs and pushes to the `main` branch. See
`.github/workflows/test.yml`.

:::

## Testing the EDD integration

The Earthdata Download application integration (supported through the
`dat_backend/routes/earthdata_download/` routes) does not have full integration
tests defined. When major changes are made, it is important that the developer
test the full EDD workflow with the changes.

See
[Testing the EDD integration](developing_with_edd.html#testing-the-edd-integration)
for more information.
