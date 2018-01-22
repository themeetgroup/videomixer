#!/usr/bin/env python3

import asyncio
import gbulb
from aiohttp import web
import sys
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
from gi.repository import GObject, Gst, GstBase, GObject, GLib
import rtmpsource
import videomixer

class Mix:
    input_test_url = 'rtmp://stream-0-stage.taggedvideo.com/live/mishatest1'
    input_test_url2 = 'rtmp://stream-0-stage.taggedvideo.com/live/mishatest2'
    input_testpattern_url = 'rtmp://stream-0-stage.taggedvideo.com/live/testpattern'
    output_test_url = 'rtmp://stream-0-stage.taggedvideo.com/live/rtmpsink'

    async def resize_handler(self, request):
        print(request)
        return web.Response(text="Hello")

    def make_app(self):
        app = web.Application()
        app.router.add_route('GET', '/resize', self.resize_handler)
        return app

    def __init__(self):
        Gst.init(sys.argv)

        self.started = False

        print("Creating a videomixer...")
        self.videomix = videomixer.VideoMixer(self.output_test_url)
        self.bg = self.videomix.add_rtmp_source(self.input_testpattern_url, 0, 0, 2, 1280, 720)
        self.video1 = self.videomix.add_rtmp_source(self.input_test_url, 20, 20, 10, 360, 640)
        self.video2 = self.videomix.add_rtmp_source(self.input_test_url2, 440, 20, 30, 180, 320)
        self.focus = False

        ## XXX: hackery, remove.
        GLib.timeout_add(5000, self.resize_videos)

        self.play()

        gbulb.install()
        loop = asyncio.get_event_loop()

        self.webapp = self.make_app()
        handler = self.webapp.make_handler()
        web_server = loop.create_server(handler, '0.0.0.0', 8888)

        loop.run_until_complete(web_server)
        loop.run_forever()

    def play(self):
        if self.started is False:
            self.started = True
            self.videomix.play()
            return True
        return False

    def resize_videos(self):
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
