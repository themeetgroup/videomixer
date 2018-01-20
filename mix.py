#!/usr/bin/env python3

import sys
import rtmpsource
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst, GstBase, Gtk, GObject


class Mix:
    input_test_url = 'rtmp://stream-0-stage.taggedvideo.com/live/mishatest1'
    output_test_url = 'rtmp://stream-0-stage.taggedvideo.com/live/rtmpsink'

    def __init__(self):
        Gst.init(sys.argv)

        print("Creating pipeline...")
        self.pipeline = Gst.Pipeline.new("rtmp-pipeline")

        if self.pipeline is None:
            print("Could not create pipeline. Bailing out!")
            sys.exit(1)

        print("Creating objects and adding to pipeline...")
        # XXX: this does the same as below.
        #self.pipeline = Gst.parse_launch('rtmpsrc location=rtmp://stream-0-stage.taggedvideo.com/live/mishatest1 ! flvdemux ! decodebin ! videomixer name=mix ! x264enc threads=0 ! flvmux streamable=1 ! rtmpsink location="rtmp://stream-0-stage.taggedvideo.com/live/rtmpsink live=1"')

        self.videomixer = Gst.ElementFactory.make("videomixer", "mix")
        self.pipeline.add(self.videomixer)

        self.x264enc = Gst.ElementFactory.make("x264enc", "x264enc")
        self.x264enc.set_property("threads", 0)
        self.pipeline.add(self.x264enc)

        self.flvmux = Gst.ElementFactory.make("flvmux", "flvmux")
        self.flvmux.set_property("streamable", 1)
        self.pipeline.add(self.flvmux)

        self.rtmpsink = Gst.ElementFactory.make("rtmpsink", "sink")
        self.rtmpsink.set_property("location", self.output_test_url)
        self.pipeline.add(self.rtmpsink)

        print("Linking elements")
        # Encode the output of videomixer to H.264
        ret = self.videomixer.link(self.x264enc)
        # Put the H.264 into an FLV container
        ret = ret and self.x264enc.link(self.flvmux)
        # Send the FLV to an RTMP sink
        ret = ret and self.flvmux.link(self.rtmpsink)
        # TODO: handle audio pipeline stuff, too

        if not ret:
            print("ERROR: Elements could not be linked.")
            sys.exit(1)

        rtmp_src = rtmpsource.RtmpSource(self.input_test_url,
                                         self.pipeline,
                                         self.videomixer)

        rtmp_src2 = rtmpsource.RtmpSource('rtmp://stream-0-stage.taggedvideo.com/live/testpattern', self.pipeline, self.videomixer)

        print("Playing...")
        self.pipeline.set_state(Gst.State.PLAYING)

        # wait until error or EOS
        terminate = False
        bus = self.pipeline.get_bus()
        while True:
            try:
                msg = bus.timed_pop_filtered(
                    0.5 * Gst.SECOND,
                    Gst.MessageType.ERROR | Gst.MessageType.EOS)
                if msg:
                    terminate = True
            except KeyboardInterrupt:
                terminate = True

            if terminate:
                break

        print("Terminated loop.")
        self.pipeline.set_state(Gst.State.NULL)


start=Mix()
Gtk.main()
