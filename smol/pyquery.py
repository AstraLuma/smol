"""
Exposes jQuery over websocket. Is generally pretty lazy and very async
"""
import aiohttp
from aiohttp import web
import json

class PyQueryFactory:
    def __call__(self, query):
        return PyQuery(..., query)

class PyQuery:
    def __init__(self, query):
        ...

    def __aiter__(self):
        ...

    # Wish we could have async indexing...

    def __getattr__(self, name):
        async def methodproxy(*args):
            ...
        return methodproxy

class PyQueryApp:
    @classmethod
    def setup_routes(cls, app):
        app.router.add_get('/pyq', cls._handler)

    async def on_load(self):
        """
        Override this to do things on page load
        """

    @classmethod
    async def _handler(cls, request):

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                print("Recv", json.loads(msg.data))
                ws.send_str(json.dumps({'type': 'info', 'msg': 'Hello!'}))
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' %
                      ws.exception())

        print('websocket connection closed')

        return ws

