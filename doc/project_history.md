# Background

The Data Access Tool backend service is based on the
[hermes-api](https://bitbucket.org/nsidc/hermes-api/src) project at NSIDC, which
provided a backend API for Data Access Tool data orders through an ECS-based
system.

With ECS scheduled to be decommissioned in July 2026, this new backend service
was developed to replace hermes.

This project provides some of the same functionality as hermes (e.g., the Python
download script endpoint, `/api/downloader-script`), removes some functionality
(e.g., ECS-based ordering and direct delivery to Google Drive), and adds one new
key feature: support for the NASA
[Earthdata Download](https://github.com/nasa/earthdata-download/) application.

This service went into production at NSIDC alongside the
[data-access-tool-ui](https://github.com/nsidc/data-access-tool-ui/) v3.1.0 on
April 16, 2025.

> [!NOTE] The Data Access Tool project has been referred to as "Everest" and
> "Hermes" at NSIDC. Generally speaking, "Hermes" refers to the legacy backend
> services that powered the DAT UI <3.1.0. "Everest" referred to the frontend
> UI. In practice, these terms were sometimes used interchangeably.
