#!/usr/bin/env python3

import sys
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst, GstBase, Gtk, GObject


class Main:
    def __init__(self):
        Gst.init(sys.argv)
        print("Creating objects...")
        # XXX: this does the same as below.
        #self.pipeline = Gst.parse_launch('rtmpsrc location=rtmp://stream-0-stage.taggedvideo.com/live/mishatest1 ! flvdemux ! decodebin ! videomixer name=mix ! x264enc threads=0 ! flvmux streamable=1 ! rtmpsink location="rtmp://stream-0-stage.taggedvideo.com/live/rtmpsink live=1"')
        self.rtmp_src = Gst.ElementFactory.make("rtmpsrc", "rtmpsrc0")
        self.queue = Gst.ElementFactory.make("queue", "queue")
        self.flvdemux = Gst.ElementFactory.make("flvdemux", "flv_demux")
        self.decodebin = Gst.ElementFactory.make("decodebin", "decodebin")
        self.videomixer = Gst.ElementFactory.make("videomixer", "mix")
        #colorspace = Gst.ElementFactory.make("ffmpegcolorspace")
        self.x264enc = Gst.ElementFactory.make("x264enc", "x264enc")
        self.flvmux = Gst.ElementFactory.make("flvmux", "flvmux")
        self.rtmpsink = Gst.ElementFactory.make("rtmpsink", "sink")

        print("Creating pipeline...")
        self.pipeline = Gst.Pipeline.new("rtmp-pipeline")

        if (not self.pipeline or not self.rtmp_src or not self.flvdemux
                or not self.decodebin or not self.videomixer
                or not self.x264enc or not self.flvmux
                or not self.rtmpsink):
            print("Could not create something. Exiting.")
            sys.exit(1)

        self.rtmp_src.set_property("location", "rtmp://stream-0-stage.taggedvideo.com/live/mishatest1")
        self.rtmpsink.set_property("location", "rtmp://stream-0-stage.taggedvideo.com/live/rtmpsink")
        self.flvmux.set_property("streamable", 1)
        self.x264enc.set_property("threads", 0)

        print("Adding to pipeline")
        self.pipeline.add(self.rtmp_src)
        self.pipeline.add(self.queue)
        self.pipeline.add(self.decodebin)
        self.pipeline.add(self.flvmux)
        self.pipeline.add(self.flvdemux)
        self.pipeline.add(self.videomixer)
        self.pipeline.add(self.x264enc)
        self.pipeline.add(self.rtmpsink)

        print("Linking elements")
        # TODO: handle audio pipeline stuff, too
        ret = self.rtmp_src.link(self.queue)
        ret = ret and self.queue.link(self.flvdemux)
        # We cannot link the flvdemux module to anything. We must link it dynamically.
        
        # We cannot link decodebin to videomixer, either. We must link it dynamically, after
        # flvdemux is dynamically linked to decodebin.
        ret = ret and self.videomixer.link(self.x264enc)
        ret = ret and self.x264enc.link(self.flvmux)
        ret = ret and self.flvmux.link(self.rtmpsink)

        if not ret:
            print("ERROR: Elements could not be linked.")
            sys.exit(1)

        # flvdemux should get audio and video pads from the rtmp_src.
        self.flvdemux.connect('pad-added', self.on_flvdemux_pad_added)

        print("Playing...")
        self.pipeline.set_state(Gst.State.PLAYING)

        # wait until error or EOS
        terminate = False
        bus = self.pipeline.get_bus()
        while True:
            print("Interrupt")
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

    def on_flvdemux_pad_added(self, src, new_pad):
        # TODO: handle linking audio, too.
        print(
            "Received new pad '{0:s}' from '{1:s}'".format(
                new_pad.get_name(),
                src.get_name()))

        sink_pad = self.decodebin.get_static_pad("sink")
        if (not sink_pad):
            print("ERROR: Could not get decodebin sink")
            sys.exit(1)

        # check the new pad's type
        new_pad_caps = new_pad.get_current_caps()
        new_pad_struct = new_pad_caps.get_structure(0)
        new_pad_type = new_pad_struct.get_name()

        if new_pad_type.startswith("audio/x-raw"):
            #sink_pad = self.audio_convert.get_static_pad("sink")
            print("Got audio pad")
        elif new_pad_type.startswith("video/x-h264"):
            #sink_pad = self.video_convert.get_static_pad("sink")
            print("Got video pad")
        else:
            print(
                "It has type '{0:s}' which is not raw audio/video. Ignoring.".format(new_pad_type))
            return

        if (sink_pad.is_linked()):
            print("sink_pad is already linked")
            return

        ret = new_pad.link(sink_pad)
        if not ret == Gst.PadLinkReturn.OK:
            print("Link failed.")

        print("Linked video pad")

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

start=Main()
Gtk.main()
