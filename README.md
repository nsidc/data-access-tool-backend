<p align="center">
  <img alt="NSIDC logo" src="https://nsidc.org/themes/custom/nsidc/logo.svg" width="150" />
</p>

# Data Access Tool (DAT) Backend

Backend services for the
[Data Access Tool UI](https://github.com/nsidc/data-access-tool-ui).

The DAT Backend is composed of:

- A Flask-based API provides endpoints that power the
  [Data Access Tool UI](https://github.com/nsidc/data-access-tool-ui). For
  example,

  - The`/api/download_script` endpoint provides the `python_script.py` download
    script for data granules matching a user's filters.
  - The `/api/get-links/` endpoint that provides the
    [getLinks](https://github.com/nasa/earthdata-download/blob/main/docs/GET_LINKS.md)
    service required for DAT integration with the
    [NASA Earthdata Downloader](https://github.com/nasa/earthdata-download).

- Docker compose configuration for the DAT backend, which includes
  [nginx proxy server configuration](./nginx).

## Level of Support

This repository is fully supported by NSIDC. If you discover any problems or
bugs, please submit an Issue. If you would like to contribute to this
repository, you may fork the repository and submit a pull request.

See the [LICENSE](LICENSE) for details on permissions and warranties. Please
contact nsidc@nsidc.org for more information.

## Requirements

- [Docker](https://www.docker.com/) and
  [docker compose](https://docs.docker.com/compose/)
- Access to NSIDC's internal Virtual Machine infrastructure. It is expected that
  this backend system be deployed via the
  [data-access-tool-vm](https://github.com/nsidc/data-access-tool-ui) project.

## Background

This service was originally a part of the
[hermes-api](https://bitbucket.org/nsidc/hermes-api/src). It was moved to a
standalone service to support the decommissioning of ECS and the rest of the
hermes stack planned for July 2026.

## Contributing

See [./doc/DEVELOPMENT.md](./doc/DEVELOPMENT.md).

## Credit

This content was developed by the National Snow and Ice Data Center with funding
from multiple sources.
