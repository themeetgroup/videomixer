#!/usr/bin/env bash

if [ $# < 1 ]; then
    echo "Usage: $0 [rtmp URL]"
    exit 1
fi

URI=$1

ffmpeg -stats -re -f lavfi -i aevalsrc="sin(400*2*PI*t)" -f lavfi -i testsrc=size=1280x720:rate=30 -vcodec libx264 -b:v 500k -c:a aac -b:a 64k -vf "format=yuv420p" -x264opts keyint=60:min-keyint=60:scenecut=-1 -f flv "$URI"
