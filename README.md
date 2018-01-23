videomixer
==========
videomixer is a Python HACKD POC to demonstrate video streaming middleware using the GStreamer library.

It runs a web server on port 8888 and provides RTMP mixing functionality.

The `/create/{stream_id}` endpoint allows to create a new stream.

E.g.:

    $ curl -H "Content-Type: application/json" -X POST  -d '{"bg_uri":"rtmp://stream-0-stage.taggedvideo.com/live/testpattern", "output_uri":"rtmp://stream-0-stage.taggedvideo.com/live/rtmpsink"}' http://localhost:8888/create/asdf

The '/add_stream/{stream_id}' endpoint allows to add streams to extant streams.

E.g.:

    $ curl -H "Content-Type: application/json" -X POST  -d '{"stream_uri":"rtmp://stream-0-stage.taggedvideo.com/live/mishatest1","x":20, "y":20, "z":101}' http://localhost:8888/add_stream/asdf

