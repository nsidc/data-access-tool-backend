# v0.4.0

- Reorganize code to make it clearer what routes serve EDD vs the python script.
- Improve Swagger API docs.
- Update python script's `cmr_filter_urls` to exclude `s3credentails` metadata
  files.
- Add volume for persistent server (nginx) logs to `docker-compose.yml` (DA-105)

# v0.3.0

- Add flask-cors, using the same config that hermes-api did. Allow all nsidc.org
  domains.
- Add `/api/status` endpoint for ops (DA-106).

# v0.2.0

- Include nginx image build and configuration.

# v0.1.0

- Initial release. This consititues an MVP for the DAT backend and includes
  support for:
  - Python script endpoint
  - get-links and Earthdata auth endpoints for supporting the DAT's NASA
    Earthdata Download option
    (<https://github.com/nsidc/data-access-tool-ui/pull/5>).
