# Contributing

- Strive to create [tests](testing.md) for all new features/bugfixes.
- New or modified features should be accompanied by adequate
  [documentation](docs.md).
- Follow the recommended
  [git flow](https://docs.github.com/en/get-started/using-github/github-flow#following-github-flow).

# Setting up a dev environment

## Development on a dev VM at NSIDC

This is the recommended approach to development. See the
[data-access-tool-vm](https://github.com/nsidc/data-access-tool-vm) project
documentation for how to get setup.

## Local development

Local development (not on an NISDC development VM) is not recommended. However,
it is possible.

### Conda environment

It can be useful to install the `dat-backend` conda environment locally so that
tools like `quarto` and `bump-my-version` can be used. To do so,

```bash
conda env create -f environment.yml
conda activate dat-backend
```

### Docker stack

The `docker-compose.local.yml` can be used to run the stack locally:

::: {.callout-note}

You will have to manually setup necessary [Environment Variables](envvars.md)
first.

:::

```bash
ln -s docker-compose.local.yml docker-compose.override.yml
docker compose up -d
```

Now you should be able to visit the API documentation page at
<https://localhost/>.

::: {.callout-note}

Docker logs can be followed via:

```bash
docker compose logs -f
```

:::
