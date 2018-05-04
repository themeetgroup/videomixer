videomixer
==========
videomixer is a Python HACKD POC to demonstrate video streaming middleware using the GStreamer library.

It runs a web server on port 8888 and provides RTMP mixing functionality. The easiest way to run it is via the Dockerfile. Make sure to have Docker installed and then you can run `./run.sh`

Using the Docker container is highly recommended since the base image contains all the proper GStreamer libraries and plugins required for things to work.

API
===

The `/stream/{stream_id}` endpoint allows to create a new stream using `PUT`

It requires the `stream_id` in the URL as well as a `bg_uri` and an `output_uri`. The `stream_id` will be used to identify this stream for future requests.

`bg_uri` - the RTMP stream that will be the background of this stream

`output_uri` - the destination RTMP stream URI

E.g.:

    $ curl -H "Content-Type: application/json" -X PUT  \
      -d '{"bg_uri":"rtmp://rtmpserver/live/testpattern",
           "output_uri":"rtmp://rtmpserver/live/rtmpsink"}' \
      http://localhost:8888/stream/asdf

The `/stream/{stream_id}/{pip_id}` endpoint allows to add streams as PiP (Picture in Picture) to extant streams using `PUT`

It requires the `stream_id` and `pip_id` in the URL as well, as well as `stream_uri`, `x`, `y`, and `z`. The `pip_id` in combination with the `stream_id` will be used to identify this PiP stream in future requests.

`stream_uri` - the RTMP stream that will be added to this stream

`x` - The beginning X coordinate to place the video onto (default 0)

`y` - The beginning Y coordinate to place the video onto (default 0)

`z` - The Z-index of the stream (default 1, background is 0)

E.g.:

    $ curl -H "Content-Type: application/json" -X PUT  \
      -d '{"stream_uri":"rtmp://rtmpserver/live/mishatest1",
           "x":20, "y":20, "z":101}' \
      http://localhost:8888/stream/asdf/pipstream1


TODO
====
* Audio pipelines
 - Audio focus
 - Audio normalization
 - Audio combination
* Finish all the APIs
* API docs
* More example scripts
