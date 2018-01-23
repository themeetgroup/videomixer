#!/usr/bin/env bash
set -xue

./build.sh

docker kill videomixer || true
docker rm videomixer || true

docker run -d \
       -p 8888:8888 \
       --name videomixer \
       -t videomixer-image
