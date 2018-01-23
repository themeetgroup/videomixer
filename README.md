videomixer
==========
videomixer is a Python HACKD POC to demonstrate video streaming middleware using the GStreamer library.

It runs a web server on port 8888 and provides RTMP mixing functionality.

The `/stream/{stream_id}` endpoint allows to create a new stream using `PUT`

It requires the `stream_id` in the URL as well as a `bg_uri` and an `output_uri`

`bg_uri` - the RTMP stream that will be the background of this stream

`output_uri` - the destination RTMP stream URI

E.g.:

    $ curl -H "Content-Type: application/json" -X PUT  -d '{"bg_uri":"rtmp://stream-0-stage.taggedvideo.com/live/testpattern", "output_uri":"rtmp://stream-0-stage.taggedvideo.com/live/rtmpsink"}' http://localhost:8888/stream/asdf

The `/stream/{stream_id}/{pip_id}` endpoint allows to add streams as PiP (Picture in Picture) to extant streams using `PUT`

It requires the `stream_id` and `pip_id` in the URL as well, as well as `stream_uri`, `x`, `y`, and `z`

`stream_uri` - the RTMP stream that will be added to this stream

`x` - The beginning X coordinate to place the video onto (default 0)

`y` - The beginning Y coordinate to place the video onto (default 0)

`z` - The Z-index of the stream (default 1, background is 0)

E.g.:

    $ curl -H "Content-Type: application/json" -X PUT  -d '{"stream_uri":"rtmp://stream-0-stage.taggedvideo.com/live/mishatest1","x":20, "y":20, "z":101}' http://localhost:8888/stream/asdf/pipstream1
