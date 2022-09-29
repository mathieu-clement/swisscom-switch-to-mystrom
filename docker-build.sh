#!/bin/sh
set -eu

cd "$(dirname $0)"
docker buildx build --platform linux/amd64 --push -t mathieuclement/swisscom-switch-to-mystrom:latest --no-cache -f Dockerfile .
