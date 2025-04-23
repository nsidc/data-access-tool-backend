# NEXT_RELEASE

- Improved documentation
- Fixed issue with docker logs: limit total amount of logs retained by Docker.
  This prevents a VM's local disk from completely filling after long enough
  uptime.
- Fix issue with EDD metrics being nested under each other in the `/api/metrics`
  generated-page.

# v1.0.1

- Tweak nginx access logs to show `x_forwarded_for` information, allowing
  metrics on unique IP addresses.

# v1.0.0

- Add metrics endpoint to show number of interactions with DAT backend.
- Tweak EDD Auth Callback HTML page text to be consistent with DAT-UI generated
  page.
- Initial "production" release

# v0.5.0

- Remove nginx configuration to serve Earthdata Download pre-release. This
  served a pre-release of the EDD necessary for testing prior to the release of
  EDD v1.0.4

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
