"""
Exposes jQuery over websocket. Is generally pretty lazy and very async
"""
import asyncio
import aiohttp
from aiohttp import web
import json
import queue

__all__ = 'JSError', 'errors', 'PyQueryApp'

class JSError(Exception):
    """
    An error occurred in JavaScript
    """

class _Errors:
    def __getattr__(self, name):
        vars(self)[name] = t = type(name, (JSError,), {})
        return t

errors = _Errors()

class QueryResults:
    def __init__(self, future):
        self.future = future
        self.iter = None

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.iter is None:
            resp = await self.future
            assert resp['type'] == 'results'
            self.iter = iter(resp['list'])
        try:
            # TODO: Map elements, etc to objects
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration


class PyQuery:
    def __init__(self, query, app):
        self.query = query
        self.app = app

    def __aiter__(self):
        return QueryResults(self.app._sendmessage({
            'type': 'list',
            'query': self.query,
        }))

    def __getattr__(self, name):
        async def methodproxy(*args):
            resp = await self.app._sendmessage({
                'type': 'call',
                'query': self.query,
                'method': name,
                'args': args,  # TODO: Map non-JSONable types
            })
        return methodproxy

class PyQueryApp:
    def __init__(self):
        self.theline = queue.Queue()

    def setup_routes(self, app):
        app.router.add_get('/pyq', self._handler)

    async def on_load(self):
        """
        Override this to do things on page load
        """

    async def _handler(self, request):

        self.ws = web.WebSocketResponse()
        await self.ws.prepare(request)

        async for msg in self.ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                self._recv(json.loads(msg.data))
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' %
                      ws.exception())

        print('websocket connection closed')

        return self.ws

    def _recv(self, obj):
        print("Recv", obj)
        if obj['type'] == 'load':
            asyncio.ensure_future(self.on_load())
            # Don't actually care about the results.
            # FIXME: At least log if there's an error 
            return
        fut = self.theline.get(False)
        if obj['type'] == 'error':
            err = None
            if obj['code'] == 'missing-method':
                err = AttributeError(obj['msg'])
            elif obj['code'] == 'unknown-message':
                err = RuntimeError(obj['msg'])
            elif obj['code'] == 'calling-exception':
                err = getattr(errors, obj['name'])(obj['msg'])
            fut.set_exception(err)
        else:
            fut.set_result(obj)

    async def _sendmessage(self, obj):
        self.ws.send_str(json.dumps(obj))
        f = asyncio.get_event_loop().create_future()
        self.theline.put(f)
        return await f

    def __call__(self, query):
        """
        "Executes" a query, returning a proxy object.
        """
        return PyQuery(query, self)
