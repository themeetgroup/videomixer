#!/usr/bin/env python3

from aiohttp import web
import videomixer
import json


class MixerApi:
    def __init__(self):
        self.videomixers = {}

        app = web.Application()
        print("Starting API server...")
        app.router.add_route('GET',
                             '/streams',
                             self.get_streams_handler)
        app.router.add_route('GET',
                             '/stream/{stream_id}',
                             self.get_stream_handler)
        app.router.add_route('PUT',
                             '/stream/{stream_id}',
                             self.create_handler)
        app.router.add_route('PUT',
                             '/stream/{stream_id}/{pip_id}',
                             self.add_stream_handler)
        app.router.add_route('POST',
                             '/stream/{stream_id}/resize/{pip_id}',
                             self.resize_handler)
        app.router.add_route('POST',
                             '/stream/{stream_id}/move/{pip_id}',
                             self.move_pip_handler)
        # TODO: implement these.
        app.router.add_route('DELETE',
                             '/stream/{stream_id}/{pip_id}',
                             self.remove_pip_handler)
        app.router.add_route('DELETE',
                             '/stream/{stream_id}',
                             self.delete_handler)
        self.app = app

    def get_handler(self):
        return self.app.make_handler()

    def get_streams_handler(self, request):
        streams = []
        for stream_id in self.videomixers.keys():
            streams.append(stream_id)
        return web.Response(text=json.dumps(streams))

    def add_stream_handler(self, request):
        stream_id = request.match_info.get('stream_id')
        pip_id = request.match_info.get('pip_id')

        if stream_id in self.videomixers:
            print("Found stream {}".format(stream_id))
        else:
            print("Could not find stream {}".format(stream_id))
            return web.Response(text=self.fail_status())

        body = yield from request.json()
        stream_uri = body['stream_uri']
        # default to the origin (0, 0)
        xpos = body['x'] if 'x' in body else 0
        ypos = body['y'] if 'y' in body else 0
        # default to z=1 (background has z=0)
        zpos = body['z'] if 'z' in body else 1

        mixer = self.videomixers[stream_id]['mixer']
        mixer.add_rtmp_source(pip_id, stream_uri, xpos, ypos, zpos)
        # kick off the new source
        mixer.play()

        return web.Response(text=self.ok_status())

    def resize_handler(self, request):
        stream_id = request.match_info.get('stream_id')
        pip_id = request.match_info.get('pip_id')

        if stream_id in self.videomixers:
            print("Found stream")
        else:
            print("Could not find stream {}".format(stream_id))
            return web.Response(text=self.fail_status())

        body = yield from request.json()
        width = body['width']
        height = body['height']

        self.videomixers[stream_id].resize(pip_id, width, height)

        return web.Response(text=self.ok_status())

    def move_pip_handler(self, request):
        stream_id = request.match_info.get('stream_id')
        pip_id = request.match_info.get('pip_id')

        if stream_id in self.videomixers:
            print("Found stream {}".format(stream_id))
        else:
            print("Could not find stream {}".format(stream_id))
            return web.Response(text=self.fail_status())

        body = yield from request.json()
        xpos = body['x']
        ypos = body['y']
        zpos = body['z']

        self.videomixers[stream_id].move(pip_id, x, y, z)

        return web.Response(text=self.ok_status())

    def remove_pip_handler(self, request):
        stream_id = request.match_info.get('stream_id')
        pip_id = request.match_info.get('pip_id')

        if stream_id in self.videomixers:
            print("Found stream {}".format(stream_id))
        else:
            print("Could not find stream {}".format(stream_id))
            return web.Response(text=self.fail_status())

        return web.Response(text=self.ok_status())

    def get_stream_handler(self, request):
        stream_id = request.match_info.get('stream_id')

        if stream_id in self.videomixers:
            print("Found stream {}".format(stream_id))
        else:
            print("Could not find stream {}".format(stream_id))
            return web.Response(text=self.fail_status())

        mixer = self.videomixers[stream_id]
        ret = {}
        ret['stream_id'] = stream_id
        ret['mixer'] = mixer.get_info()

        return web.Response(text=json.dumps(ret))

    def delete_handler(self, request):
        stream_id = request.match_info.get('stream_id')

        if stream_id in self.videomixers:
            print("Found stream {}".format(stream_id))
        else:
            print("Could not find stream {}".format(stream_id))
            return web.Response(text=self.fail_status())

        return web.Response(text=self.ok_status())

    def create_handler(self, request):
        stream_id = request.match_info.get('stream_id')

        if stream_id in self.videomixers:
            print("Stream {} already exists".format(stream_id))
            return web.Response(text=self.fail_status())

        body = yield from request.json()
        print("Creating new stream {}".format(stream_id))
        output_uri = body['output_uri']
        bg_uri = body['bg_uri']
        print("Creating a videomixer for stream_id={} {} -> {}...".format(
              stream_id,
              bg_uri,
              output_uri))

        mixer = videomixer.VideoMixer(output_uri)
        mixer.add_rtmp_source('bg', bg_uri)
        mixer.play()
        # Keep track of the mixer for future requests
        self.videomixers[stream_id] = mixer

        return web.Response(text=self.ok_status())

    def ok_status(self):
        return json.dumps({'status': 'OK'})

    def fail_status(self):
        return json.dumps({'status': 'FAIL'})
