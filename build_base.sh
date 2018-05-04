#!/usr/bin/env bash
set -xue
VERSION=1.0

docker build -t videomixer-base -f Dockerfile.base .
