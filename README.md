# Data Access Tool (DAT) Backend

Backend services for the
[Data Access Tool UI](https://github.com/nsidc/data-access-tool-ui).

This repository provides:

- A Flask-based API provides:

* The`python_script.py` download script for data granules matching a user's
  filters.
* The
  [getLinks](https://github.com/nasa/earthdata-download/blob/main/docs/GET_LINKS.md)
  service required for DAT integration with the
  [NASA Earthdata Downloader](https://github.com/nasa/earthdata-download).

- Docker compose configuration for the DAT backend, which includes
  [nginx server configuration](./nginx).

## Background

This service was originally a part of the
[hermes-api](https://bitbucket.org/nsidc/hermes-api/src). It was moved to a
standalone service to support the decommissioning of ECS and the rest of the
hermes stack planned for July 2026.

## Contributing

See [./doc/DEVELOPMENT.md](./doc/DEVELOPMENT.md).
