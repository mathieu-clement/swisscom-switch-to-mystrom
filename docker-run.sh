#!/bin/sh
set -eu

docker run -e "REAL_HOST=192.168.0.25" -e "LISTEN_HOST=127.0.0.1" -e "LISTEN_PORT=5005" --rm -p 5005:5005 --name swisscom mathieuclement/swisscom-switch-to-mystrom:latest
