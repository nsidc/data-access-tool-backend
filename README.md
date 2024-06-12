# Data Access Tool (DAT) downloader script service

This repository contains code for a service that provides the [Data Access Tool
(AKA Everest UI)](https://bitbucket.org/nsidc/everest-ui/) with a python-based download script for data granules
matching a user's filters.

This service was originally a part of the
[hermes-api](https://bitbucket.org/nsidc/hermes-api/src). It was moved to a
standalone service to support the decomissioning of ECS and the rest of the
hermes stack planned for July 2026.


## Dev

### Testing

To test the python script template code itself:

```
PYTHONPATH=./src/ pytest test/
```
