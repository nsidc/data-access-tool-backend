#!/bin/bash

set -e

docker compose -f docker-compose-test.yml build 
docker compose -f docker-compose-test.yml run --rm api
