#!/usr/bin/env bash
set -xue
VERSION=1.0

docker build -t videomixer-base -f Dockerfile.base .
docker tag  videomixer-base dockerregistry.tagged.com/video/videomixer:${VERSION}
docker push dockerregistry.tagged.com/video/videomixer:${VERSION}
