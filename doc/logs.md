# Logs

The Data Access Tool backend produces logs from two primary sources:

- Flask/API application logs produced through the use of e.g., `app.logger.info`
  and unhandled exceptions.
  - In dev, the Flask dev server produces logs that can be viewed with
    `docker compose logs`.
  - In non-dev environments, the `gunicorn` server produces logs that can be
    viewed with `docker compose logs`.
- NGINX `error` and `access` server logs, which are written to local disk.

## NGINX Server logs

Logs are written to local disk, in `./logs/server/`.

It is expected that these logs be backed-up to a networked share drive (defined
through the `LOGS_SHARE_PATH` [environment variable](envvars.md)) through
`logrotation`. The `dat.access.log` is intended to be used for application
metrics, and these data should be retained for recordkeeping. The
[data-access-tool-vm](https://github.com/nsidc/data-access-tool-vm) project sets
up logrotation for NSIDC deployments.

Each line of the NGINX access logs are formatted as JSON so that the
`/api/metrics` endpoint can easily parse the records.

An example line from an access log:

```json
{
  "http_user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0",
  "args": "",
  "uri": "/api/status",
  "http_referer": "https://dev.data-access-tool.trst2284.dev.int.nsidc.org/",
  "body_bytes_sent": "551",
  "status": "200",
  "request": "GET /api/status HTTP/1.1",
  "time_iso8601": "2025-04-14T14:31:03+00:00",
  "remote_addr": "111.111.111.111",
  "x_forwarded_for": "12.345.678.911, 111.111.111.111"
}
```
