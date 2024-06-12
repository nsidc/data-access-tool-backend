# Data Access Tool (DAT) downloader script service

This repository contains code for a service that provides the [Data Access Tool
(AKA Everest UI)](https://bitbucket.org/nsidc/everest-ui/) with a python-based download script for data granules
matching a user's filters.

This service was originally a part of the
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
