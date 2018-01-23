#!/usr/bin/env python3

import sys
import rtmpsource
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
from gi.repository import GObject, Gst, GstBase, GObject


class VideoMixer:

    def __init__(self, output_url):
        self.output_url = output_url
        self.initialize()

    def play(self):
        print("Playing...")
        self.pipeline.set_state(Gst.State.PLAYING)
        return

    def pause(self):
        print("Pausing...")
        self.pipeline.set_state(Gst.State.PAUSED)
        return

    def add_rtmp_source(self, location, xpos=0, ypos=0, zorder=0, width=None, height=None):
        rtmp_src = rtmpsource.RtmpSource(location,
                                         self.pipeline,
                                         self.videomixer,
                                         xpos, ypos, zorder, width, height)
        return rtmp_src

    def initialize(self):
        print("Creating pipeline...")
        self.pipeline = Gst.Pipeline.new("rtmp-pipeline")

        if self.pipeline is None:
            print("Could not create pipeline. Bailing out!")
            sys.exit(1)

        print("Creating objects and adding to pipeline...")
        self.videomixer = Gst.ElementFactory.make("videomixer", "mix")
        self.pipeline.add(self.videomixer)

        self.x264enc = Gst.ElementFactory.make("x264enc", "x264enc")
        self.x264enc.set_property("threads", 0)
        self.pipeline.add(self.x264enc)

        self.flvmux = Gst.ElementFactory.make("flvmux", "flvmux")
        self.flvmux.set_property("streamable", 1)
        self.pipeline.add(self.flvmux)

        self.rtmpsink = Gst.ElementFactory.make("rtmpsink", "sink")
        self.rtmpsink.set_property("location", self.output_url)
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
            raise Exception("Could not link elements in videomixer")

