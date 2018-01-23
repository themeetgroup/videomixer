#!/usr/bin/env python3

import asyncio
import gbulb
from aiohttp import web
import json
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

    def make_app(self):
        app = web.Application()
        app.router.add_route('POST', '/resize/{stream_id}', self.resize_handler)
        app.router.add_route('POST', '/create/{stream_id}', self.create_handler)
        app.router.add_route('POST', '/add_stream/{stream_id}', self.add_stream_handler)
        app.router.add_route('DELETE', '/delete/{stream_id}', self.delete_handler)
        return app

    def add_stream_handler(self, request):
        stream_id = request.match_info.get('stream_id')
        if stream_id in self.videomixers:
            print("Found stream")
        else:
            print("Could not find stream {}".format(stream_id))
            return web.Response(text='{"status": "FAIL"}')
        return web.Response(text='{"status": "OK"}')

    def resize_handler(self, request):
        stream_id = request.match_info.get('stream_id')
        if stream_id in self.videomixers:
            print("Found stream")
        else:
            print("Could not find stream {}".format(stream_id))
            return web.Response(text='{"status": "FAIL"}')
        return web.Response(text='{"status": "OK"}')

    def delete_handler(self, request):
        stream_id = request.match_info.get('stream_id')
        if stream_id in self.videomixers:
            print("Found stream")
        else:
            print("Could not find stream {}".format(stream_id))
            return web.Response(text='{"status": "FAIL"}')
        return web.Response(text='{"status": "OK"}')

    def create_handler(self, request):
        stream_id = request.match_info.get('stream_id')
        if stream_id in self.videomixers:
            print("Stream {} already exists".format(stream_id))
            return web.Response(text='{"status": "FAIL"}')

        body = yield from request.json()
        print("Creating new stream {}".format(stream_id))
        output_uri = body['output_uri']
        bg_uri = body['bg_uri']
        print("Creating a videomixer for {} -> {}...".format(bg_uri, output_uri))
        self.videomixers[stream_id] = {}
        mixer =  videomixer.VideoMixer(self.output_test_url)
        self.videomixers[stream_id]['mixer'] = mixer
        self.videomixers[stream_id]['bg'] = mixer.add_rtmp_source(self.input_testpattern_url, 0, 0, 100)
        mixer.play()
        return web.Response(text="{'status': 'OK'}")

    def __init__(self):
        Gst.init(sys.argv)

        self.videomixers = {}
        gbulb.install()
        loop = asyncio.get_event_loop()

        self.webapp = self.make_app()
        handler = self.webapp.make_handler()
        web_server = loop.create_server(handler, '0.0.0.0', 8888)

        loop.run_until_complete(web_server)
        loop.run_forever()

start = Mix()
