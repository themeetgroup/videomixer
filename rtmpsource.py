#!/usr/bin/env python3

import sys
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst, GstBase, Gtk, GObject


class RtmpSource:
    def __init__(self, location, pipeline, videomixer):
        # RTMP stream location
        self.location = location
        # GStreamer Pipeline to attach to
        self.pipeline = pipeline
        # The videomixer to output to
        self.videomixer = videomixer

        self.initialize()

    def initialize(self):
        # Create and hook up relevant objects
        print("Creating RtmpSource objects")
        # TODO: handle audio pipeline stuff, too
        self.rtmp_src = Gst.ElementFactory.make("rtmpsrc", "rtmpsrc-" + self.location)
        self.rtmp_src.set_property("location", self.location)
        self.pipeline.add(self.rtmp_src)

        self.queue = Gst.ElementFactory.make("queue")
        self.pipeline.add(self.queue)

        self.flvdemux = Gst.ElementFactory.make("flvdemux")
        self.pipeline.add(self.flvdemux)

        self.decodebin = Gst.ElementFactory.make("decodebin")
        self.pipeline.add(self.decodebin)
        
        # Link the RTMP source to a queue
        ret = self.rtmp_src.link(self.queue)
        # Link the queue to an FLV demuxer
        ret = ret and self.queue.link(self.flvdemux)

        if not ret:
            print("ERROR: Elements could not be linked.")
            raise Exception("Could not link elements in RtmpSource")

        # flvdemux should get audio and video pads from the rtmp_src.
        # We cannot link the flvdemux module to decodebin. We must link it
        # dynamically once the pads appear.
        # We cannot link decodebin to videomixer, either. We must link it
        # dynamically, after flvdemux is dynamically linked to decodebin and
        # the pad appears in decodebin.
        self.flvdemux.connect('pad-added', self.on_flvdemux_pad_added)

    def on_flvdemux_pad_added(self, src, new_pad):
        # TODO: handle linking audio, too.
        sink_pad = None
        print(
            "Received new pad '{0:s}' from '{1:s}'".format(
                new_pad.get_name(),
                src.get_name()))

        # check the new pad's type
        new_pad_caps = new_pad.get_current_caps()
        new_pad_struct = new_pad_caps.get_structure(0)
        new_pad_type = new_pad_struct.get_name()

        if new_pad_type.startswith("audio"):
            print("Got audio pad. Not currently handling it.")
            return
        elif new_pad_type.startswith("video/x-h264"):
            print("Got video pad")
            sink_pad = self.decodebin.get_static_pad("sink")
        else:
            print(
                "It has type '{0:s}' which is not raw audio/video. Ignoring.".format(new_pad_type))
            return

        if sink_pad is None:
            print("No sink_pad defined. Bailing out.")
            return

        if (sink_pad.is_linked()):
            print("sink_pad is already linked")
            return

        ret = new_pad.link(sink_pad)
        if not ret == Gst.PadLinkReturn.OK:
            print("Link failed.")
            return

        print("Linked {0:s} pad".format(new_pad.get_name()))

        # Next we listen for the "src_0" pad to appear from decodebin, so we can hook it up
        # to the videomixer component.
        self.decodebin.connect("pad-added", self.on_decode_pad_added)

    def on_decode_pad_added(self, src, new_pad):
        print(
            "Received new decodebin pad '{0:s}' from '{1:s}'".format(
                new_pad.get_name(),
                src.get_name()))

        # Get a sink pad and link it
        videomixer_sink_pad_template = self.videomixer.get_pad_template("sink_%u")
        videomixer_sink = self.videomixer.request_pad(videomixer_sink_pad_template, None, None)

        if (videomixer_sink is None):
            print("Could not get videomixer sink!")
            return

        new_pad.link(videomixer_sink)
