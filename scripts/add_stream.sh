#!/usr/bin/env bash

INSTANCE=$1
STREAM_ID=$2
PIP_ID=$3
PIP_URI=$4
XPOS=$5
YPOS=$6
ZPOS=$7

curl -H "Content-Type: application/json" -X PUT  -d "{\"stream_uri\":\"${PIP_URI}\", \"x\":\"${XPOS}\", \"y\":\"${YPOS}\",\"z\":\"${ZPOS}\"}" http://${INSTANCE}:8888/stream/${STREAM_ID}/${PIP_ID}
