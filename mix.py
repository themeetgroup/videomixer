#!/usr/bin/env python3

import sys
import rtmpsource
import videomixer
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst, GstBase, Gtk, GObject, GLib


class Mix:
    input_test_url = 'rtmp://stream-0-stage.taggedvideo.com/live/mishatest1'
    input_test_url2 = 'rtmp://stream-0-stage.taggedvideo.com/live/mishatest2'
    input_testpattern_url = 'rtmp://stream-0-stage.taggedvideo.com/live/testpattern'
    output_test_url = 'rtmp://stream-0-stage.taggedvideo.com/live/rtmpsink'

    def __init__(self):
        Gst.init(sys.argv)

        self.started = False

        print("Creating a videomixer...")
        self.videomix = videomixer.VideoMixer(self.output_test_url)
        self.bg = self.videomix.add_rtmp_source(self.input_testpattern_url, 0, 0, 2, 1280, 720)
        self.video1 = self.videomix.add_rtmp_source(self.input_test_url, 20, 20, 10, 360, 640)
        self.video2 = self.videomix.add_rtmp_source(self.input_test_url2, 440, 20, 30, 180, 320)
        self.focus = False

    def play(self):
        if self.started is False:
            self.started = True
            self.videomix.play()
            return True
        return False

    def move_videos(self):
        #self.video1.move(40, 0)
        #self.video2.move(40, 0)
        if self.focus is False:
            self.video1.resize(180, 320)
            self.video2.resize(360, 640)
            self.focus = True
        else:
            self.video1.resize(360, 640)
            self.video2.resize(180, 320)
            self.focus = False
        return True

start = Mix()
GLib.timeout_add(5000, start.move_videos)
start.play()
Gtk.main()
# asyncio -- preferred. transforms async event driven code into seq code.
#            explicit async boundaries. non-blocking i/o server.
# idle add (Gtk) -- post to main loop using g_idle_add ?
