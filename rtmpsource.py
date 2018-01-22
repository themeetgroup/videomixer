#!/usr/bin/env python3

import sys
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst, GstBase, Gtk, GObject


class RtmpSource:
    def __init__(self, location, pipeline, videomixer, xpos, ypos, zorder, width, height):
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

        self.is_live = False

        self.initialize()

    def initialize(self):
        # Create and hook up relevant objects
        print("Creating RtmpSource objects")
        # TODO: handle audio pipeline stuff, too
        self.rtmp_src = Gst.ElementFactory.make("rtmpsrc")
        self.rtmp_src.set_property("location", self.location)
        self.pipeline.add(self.rtmp_src)

        self.queue = Gst.ElementFactory.make("queue")
        self.pipeline.add(self.queue)

        self.flvdemux = Gst.ElementFactory.make("flvdemux")
        self.flvdemux.connect("pad-added", self.on_flvdemux_pad_added)
        self.pipeline.add(self.flvdemux)

        self.decodebin = Gst.ElementFactory.make("decodebin")
        self.decodebin.connect("pad-added", self.on_decode_pad_added)
        self.pipeline.add(self.decodebin)

        self.videoscale = Gst.ElementFactory.make("videoscale")
        self.pipeline.add(self.videoscale)

        self.capsfilter = Gst.ElementFactory.make("capsfilter")
        self.vidcaps = Gst.Caps.from_string("video/x-raw,width={},height={}".format(self.width, self.height))
        self.capsfilter.set_property("caps", self.vidcaps)
        self.pipeline.add(self.capsfilter)

        # Link the RTMP source to a queue
        ret = self.rtmp_src.link(self.queue)
        # Link the queue to an FLV demuxer
        ret = ret and self.queue.link(self.flvdemux)

        ret = ret and self.videoscale.link(self.capsfilter)
        #ret = ret and self.capsfilter.link(self.videomixer)
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
        (ok, self.video_width) = video_pad_caps.get_structure(0).get_int("width")
        (ok, self.video_height) = video_pad_caps.get_structure(0).get_int("height")

        scale_sink = self.videoscale.get_static_pad("sink")
        scale_src = self.capsfilter.get_static_pad("src")

        # Get a sink pad from the mixer
        pad_template = self.videomixer.get_pad_template("sink_%u")
        sink = self.videomixer.request_pad(pad_template, None, None)

        if (sink is None):
            print("Could not get videomixer sink!")
            return

        # Set the sink position if applicable
        if (self.xpos > 0 and self.ypos > 0):
            sink.set_property("xpos", self.xpos)
            sink.set_property("ypos", self.ypos)

        # Set zorder (z-index)
        sink.set_property("zorder", self.zorder)

        # Link the video to the videomixer sink
        ret = new_pad.link(scale_sink)
        scale_src.link(sink)

        if ret is None:
            print("Could not hook up new pad to videomixer sink")
            raise Exception("Failed to hook up decode sink to videomixer")

        self.videomixer_sink = sink
        self.is_live = True

    def set_position(self, xpos, ypos, zorder):
        self.xpos = xpos
        self.ypos = ypos
        self.zorder = zorder

        self.videomixer_sink.set_property("xpos", self.xpos)
        self.videomixer_sink.set_property("ypos", self.ypos)
        self.videomixer_sink.set_property("zorder", self.zorder)

    def move(self, xdiff, ydiff, zdiff=0):
        if self.is_live is False:
            return

        # XXX: magic numbers
        self.xpos += xdiff;
        self.xpos %= 1280
        self.ypos += ydiff;
        self.ypos %= 720
        self.zorder += zdiff

        self.videomixer_sink.set_property("xpos", self.xpos)
        self.videomixer_sink.set_property("ypos", self.ypos)
        self.videomixer_sink.set_property("zorder", self.zorder)

    def resize(self, width, height):
        if self.is_live is False:
            return

        caps = Gst.Caps.from_string("video/x-raw,width={},height={}".format(width, height))
        print(caps)
        self.capsfilter.set_property("caps", caps)

    def is_live(self):
        return self.is_live
