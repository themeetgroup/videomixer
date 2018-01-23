#!/usr/bin/env bash

INSTANCE=$1
STREAM_ID=$2
BG_URI=$3
OUTPUT_URI=$4

curl -H "Content-Type: application/json" -X PUT  -d "{\"bg_uri\":\"${BG_URI}\", \"output_uri\":\"${OUTPUT_URI}\"}" ${INSTANCE}:8888/create/${STREAM_ID}
