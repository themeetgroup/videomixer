#!/usr/bin/env bash

./build.sh

docker kill nginx-rtmp || true
docker rm nginx-rtmp || true

docker run -d \
       -p 1935:1935 \
       -p 8890:8890 \
       --name nginx-rtmp \
       -t nginx-rtmp
