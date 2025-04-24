# Environment Variables

Environment variables are used to configure the DAT backend at runtime. These
environment variables are provided via NSIDC's
[Vault](https://www.hashicorp.com/en/products/vault) instance via virtual
machines provisioned with the
[data-access-tool-vm](https://github.com/nsidc/data-access-tool-vm) project.

Environment variables are exposed to the DAT's components through
`docker compose` configuration files. E.g., see the `docker-compose.yml`'s
`environment` sections.

- `EARTHDATA_APP_USERNAME`: DAT's Earthdata Login App username (See
  [Earthdata login](developing_with_edd.qmd#earthdata-login)).
- `EARTHDATA_APP_PASSWORD`: DAT's Earthdata Login App username (See
  [Earthdata login](developing_with_edd.qmd#earthdata-login)).
- `EARTHDATA_APP_CLIENT_ID`: DAT's Earthdata Login App client ID (See
  [Earthdata login](developing_with_edd.qmd#earthdata-login)).
- `DAT_FLASK_SECRET_KEY`: Secret key used by Flask for session management
  (required by Earthdata Auth endpoints). See
  <https://flask.palletsprojects.com/en/stable/quickstart/#sessions>.
- `LOGS_SHARE_PATH`: Local path to directory where logs are stored. See
  [Logs](logs.md) for more information.
- `LOGS_SHARE_BACKUP_PATH`: Path to directory where logs are backed-up for
  long-term storage. See [Logs](logs.md) for more information.
