#!/usr/bin/env python3

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
from gi.repository import GObject, Gst, GstBase, GObject


class RtmpSource:
    def __init__(self, location, pipeline, videomixer,
                 xpos, ypos, zorder, width, height):
        # RTMP stream location
        self.location = location
        # GStreamer Pipeline to attach to
        self.pipeline = pipeline
        # The videomixer to output to
        self.videomixer = videomixer
        # Not ready.
        self.videomixer_sink = None

        self.xpos = xpos
        self.ypos = ypos
        self.zorder = zorder
        self.width = width
        self.height = height

        self.initialize()

    def initialize(self):
        # Create and hook up relevant objects
        print("Creating RtmpSource objects")
        # TODO: handle audio pipeline stuff, too
        # TODO: Look into uridecodebin ?
        self.rtmp_src = Gst.ElementFactory.make("rtmpsrc")
        self.rtmp_src.set_property("location", self.location)
        self.pipeline.add(self.rtmp_src)

        self.flvdemux = Gst.ElementFactory.make("flvdemux")
        # We listen for the pad-added event of flvdemux so that
        # we can link the demuxed pads to the rest of the pipeline.
        self.flvdemux.connect("pad-added", self.on_flvdemux_pad_added)
        self.pipeline.add(self.flvdemux)

        self.decodebin = Gst.ElementFactory.make("decodebin")
        # We listen for the pad-added event of decodebin so that
        # we can link the decoded video pad to the mixer sink.
        self.decodebin.connect("pad-added", self.on_decode_pad_added)
        self.pipeline.add(self.decodebin)

        self.videoscale = Gst.ElementFactory.make("videoscale")
        self.pipeline.add(self.videoscale)

        self.capsfilter = Gst.ElementFactory.make("capsfilter")
        # Only change the width and height if they're set. Otherwise
        # leave it unchanged. videoscale+capsfilter shouldn't do
        # anything if there aren't any caps set.
        if (self.width is not None and self.height is not None):
            caps_string = self.get_caps_string(self.width, self.height)
            self.vidcaps = Gst.Caps.from_string(caps_string)
            self.capsfilter.set_property("caps", self.vidcaps)
        self.pipeline.add(self.capsfilter)

        # Link the RTMP source to the FLV demuxer
        ret = self.rtmp_src.link(self.flvdemux)

        # Link the videoscaler to the capsfilter
        ret = ret and self.videoscale.link(self.capsfilter)

        # flvdemux should get audio and video pads from the rtmp_src.
        # We cannot link the flvdemux module to decodebin. We must link it
        # dynamically once the pads appear.
        # We cannot link decodebin to videomixer, either. We must link it
        # dynamically, after flvdemux is dynamically linked to decodebin and
        # the pad appears in decodebin.

        if not ret:
            print("ERROR: Elements could not be linked.")
            raise Exception("Could not link elements in RtmpSource")

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
        elif new_pad_type.startswith("video"):
            print("Got video pad")
            sink_pad = self.decodebin.get_static_pad("sink")
        else:
            print("Type '{0:s}' which is not audio/video. Ignoring.".format(
                new_pad_type))
            return

        if sink_pad is None:
            print("No sink_pad defined. Bailing out.")
            return

        if sink_pad.is_linked():
            print("sink_pad is already linked")
            return

        ret = new_pad.link(sink_pad)
        if not ret == Gst.PadLinkReturn.OK:
            print("Link failed.")
            return

        print("Linked {0:s} pad".format(new_pad.get_name()))

    def on_decode_pad_added(self, src, new_pad):
        print(
            "Received new decodebin pad '{0:s}' from '{1:s}'".format(
                new_pad.get_name(),
                src.get_name()))

        video_pad_caps = new_pad.get_current_caps()
        caps0 = video_pad_caps.get_structure(0)
        (ok, self.video_width) = caps0.get_int("width")
        (ok, self.video_height) = caps0.get_int("height")

        # Get the sink for the videoscale module and the "src" (output) from
        # the capsfilter module.
        scale_sink = self.videoscale.get_static_pad("sink")
        filter_src = self.capsfilter.get_static_pad("src")

        # Get a sink pad from the videomixer
        pad_template = self.videomixer.get_pad_template("sink_%u")
        sink = self.videomixer.request_pad(pad_template, None, None)

        if (sink is None):
            print("Could not get videomixer sink!")
            return

        # Set the sink position
        sink.set_property("xpos", self.xpos)
        sink.set_property("ypos", self.ypos)
        # Set zorder (z-index)
        sink.set_property("zorder", self.zorder)

        # Link the decoder pad to the videoscale sink
        # The videoscale module is hooked up to the capsfilter
        # module already.
        ret = new_pad.link(scale_sink)
        # Link the capsfilter src to the videomixer sink
        filter_src.link(sink)

        if ret is None:
            print("Could not hook up new pad to videomixer sink")
            raise Exception("Failed to hook up decode sink to videomixer")

        self.videomixer_sink = sink

    def move(self, xpos, ypos, zorder):
        self.xpos = xpos
        self.ypos = ypos
        self.zorder = zorder

        self.videomixer_sink.set_property("xpos", self.xpos)
        self.videomixer_sink.set_property("ypos", self.ypos)
        self.videomixer_sink.set_property("zorder", self.zorder)

    def shift(self, xdiff, ydiff, zdiff=0):
        self.xpos += xdiff
        self.xpos %= self.video_width
        self.ypos += ydiff
        self.ypos %= self.video_height
        self.zorder += zdiff

        self.videomixer_sink.set_property("xpos", self.xpos)
        self.videomixer_sink.set_property("ypos", self.ypos)
        self.videomixer_sink.set_property("zorder", self.zorder)

    def resize(self, width, height):
        caps = Gst.Caps.from_string(self.get_caps_string(width, height))
        self.capsfilter.set_property("caps", caps)

    def get_caps_string(self, width, height):
        return "video/x-raw,width={},height={}".format(width, height)

    def get_info(self):
        ret = {}
        ret['orig_video'] = {
            'location': self.location,
            'width': self.video_width,
            'height': self.video_height
        }
        ret['video'] = {
            'width': self.width,
            'height': self.height,
            'xpos': self.xpos,
            'ypos': self.ypos,
            'zorder': self.zorder
        }
        return ret
