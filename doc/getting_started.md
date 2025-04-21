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

::: {.callout-note}

GitHub actions are configured to run pre-commit for all PRs and pushes to the
`main` branch. See `.github/workflows/pre-commit.yml`.

:::

### Running tests

Before manually running tests, setup the `EARTHDATA_USERNAME` and
`EARTHDATA_PASSWORD` envvars, which are necessary for integration tests.

Next, to run all tests:

```
scripts/run_tests.sh
```

::: {.callout-note}

GitHub actions are configured to run unit tests that do not require Earthdata
login credentials for all PRs and pushes to the `main` branch. See
`.github/workflows/test.yml`.

:::

## Releasing

To release a new version:

- Make changes on a branch
- Update CHANGELOG for next release
- Run `bump-my-version bump {major|minor|patch}`
- Open a PR and have it merged to `main` after review
- Tag latest commit on `main` with the version, and push. This will trigger a
  build of the `data-access-tool-api` and `data-access-tool-server` images with
  the given version tag.
- Deploy the latest change with the
  [data-access-tool-vm](https://github.com/nsidc/data-access-tool-vm).
