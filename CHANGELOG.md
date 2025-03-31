# v0.3.0

- Add flask-cors, using the same config that hermes-api did. Allow all nsidc.org
  domains.

# v0.2.0

- Include nginx image build and configuration.

# v0.1.0

- Initial release. This consititues an MVP for the DAT backend and includes
  support for:
  - Python script endpoint
  - get-links and Earthdata auth endpoints for supporting the DAT's NASA
    Earthdata Download option
    (<https://github.com/nsidc/data-access-tool-ui/pull/5>).
