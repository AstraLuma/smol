"""
Exposes jQuery over websocket. Is generally pretty lazy and very async
"""
import asyncio
import aiohttp
from aiohttp import web
import json
import queue


__all__ = 'JSError', 'errors', 'App'


class JSError(Exception):
    """
    An error occurred in JavaScript
    """


class _Errors:
    def __getattr__(self, name):
        vars(self)[name] = t = type(name, (JSError,), {})
        return t


errors = _Errors()


class PyQuery:
    def __init__(self, query, socket):
        self.query = query
        self.socket = socket

    def __aiter__(self):
        async def mkresults(self):
            resp = await self.socket._sendmessage({
                'type': 'list',
                'query': self.query,
            })
            assert resp['type'] == 'results'
            for i in resp['list']:
                yield i
        return mkresults()

    def __getattr__(self, name):
        async def methodproxy(*args):
            resp = await self.socket._sendmessage({
                'type': 'call',
                'query': self.query,
                'method': name,
                'args': self.socket._args2json(args),
            })
            assert resp['type'] == 'return'
            # TODO: Map elements, etc to objects
            return self.socket._json2args(resp['value'])
        return methodproxy


class Socket:
    def __init__(self):
        self.theline = queue.Queue()

    def __call__(self, query):
        """
        "Executes" a query, returning a proxy object.
        """
        return PyQuery(query, self)

    async def on_load(self):
        """
        Override this to do things on page load
        """

    @classmethod
    def __handle__(cls, request):
        self = cls()
        return self._handler(request)

    async def _handler(self, request):

        self.ws = web.WebSocketResponse()
        await self.ws.prepare(request)

        async for msg in self.ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                self._recv(json.loads(msg.data))
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' % self.ws.exception())

        print('websocket connection closed')

        return self.ws

    def _recv(self, obj):
        print("Recv", obj)
        if obj['type'] == 'load':
            asyncio.ensure_future(self.on_load())
            # Don't actually care about the results.
            # FIXME: At least log if there's an error
            return
        elif obj['type'] == 'callback':
            ...
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

    def _args2json(self, args):
        # TODO: Map non-JSONable types
        return args

    def _json2args(self, args):
        # TODO: Map non-JSONable types
        return args


class App:
    def __init__(self):
        self._calls = []

    # See https://aiohttp.readthedocs.io/en/stable/web_reference.html#aiohttp.web.UrlDispatcher.add_route
    def _reg(self, method, path, **kwargs):
        def _(func):
            if hasattr(func, '__handle__'):
                self._calls.append(
                    ((method, path, func.__handle__), kwargs)
                )
            else:
                self._calls.append(
                    ((method, path, func), kwargs)
                )
            return func
        return _

    def setup_routes(self, app):
        for pargs, kwargs in self._calls:
            app.router.add_route(*pargs, **kwargs)

    def __call__(self, path, **kwargs):
        return self._reg('*', path, **kwargs)

    def GET(self, path, **kwargs):
        return self._reg('GET', path, **kwargs)

    def POST(self, path, **kwargs):
        return self._reg('POST', path, **kwargs)

    def PUT(self, path, **kwargs):
        return self._reg('POST', path, **kwargs)

    def DELETE(self, path, **kwargs):
        return self._reg('POST', path, **kwargs)

    def PATCH(self, path, **kwargs):
        return self._reg('POST', path, **kwargs)

    # Omitting HEAD

    def OPTIONS(self, path, **kwargs):
        return self._reg('POST', path, **kwargs)
