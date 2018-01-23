#!/usr/bin/env bash

INSTANCE=$1
STREAM_ID=$2
STREAM_URI=$3
XPOS=$4
YPOS=$5
ZPOS=$6

curl -H "Content-Type: application/json" -X POST  -d "{\"stream_uri\":\"${BG_URI}\", \"x\":\"${XPOS}\", \"y\":\"${YPOS}\",\"z\":\"${ZPOS}\"}" http://${INSTANCE}:8888/add_stream/${STREAM_ID}
