#!/usr/bin/env python3

import asyncio
import gbulb
import sys
import mixerapi
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
from gi.repository import GObject, Gst, GstBase, GObject, GLib  # noqa: E402


class Mix:
    bind_addr = '0.0.0.0'
    listen_port = 8888

    def __init__(self):
        Gst.init(sys.argv)
        # Gst.debug_set_active(True)
        # Gst.debug_set_default_threshold(4)

        print("Initializing videomixer application...")
        gbulb.install()
        loop = asyncio.get_event_loop()

        self.mixerapi = mixerapi.MixerApi()
        handler = self.mixerapi.get_handler()
        web_server = loop.create_server(handler,
                                        self.bind_addr,
                                        self.listen_port)

        print("Ready! Listening on {}:{}".format(self.bind_addr,
                                                 self.listen_port))
        loop.run_until_complete(web_server)
        loop.run_forever()


start = Mix()
