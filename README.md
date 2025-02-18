# Data Access Tool (DAT) Backend

Backend services for the [Data Access Tool UI](https://github.com/nsidc/data-access-tool-ui).

A Flask-based API provides:

* The`python_script.py` download script for data granules matching a user's filters.
* TODO: The
  [getLinks](https://github.com/nasa/earthdata-download/blob/main/docs/GET_LINKS.md)
  service required for DAT integration with the [NASA Earthdata
  Downloader](https://github.com/nasa/earthdata-download).


Note that this service was originally a part of the
[hermes-api](https://bitbucket.org/nsidc/hermes-api/src). It was moved to a
standalone service to support the decomissioning of ECS and the rest of the
hermes stack planned for July 2026.


## Dev

### Testing the download script

The tests for the download script assumes a .netrc file is setup for the current
user to login to earthdata. Setup a `.netrc` with credentials for earthdata
login by e.g., [using the earthaccess
library](https://earthaccess.readthedocs.io/en/latest/howto/authenticate/)

Once a `.netrc` file is setup:

```
PYTHONPATH=./src/ pytest test/
```
