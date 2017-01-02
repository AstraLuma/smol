from aiohttp import web
import aiohttp_jinja2
import pkg_resources
from .pyq import Socket, App
import pathlib
import mimetypes

app = App()


@app.GET('/')
@aiohttp_jinja2.template('index.html')
async def index(request):
    return {}


@app.GET('/static/{filename}')
async def static(request):
    fn = request.match_info['filename']
    if '/' in fn:
        return web.Response(status=404)
    # FIXME: Handle missing file
    try:
        stream = pkg_resources.resource_stream('smol.static', fn)
    except NotImplementedError:
        p = pathlib.Path(__file__).parent / 'static' / fn
        stream = open(str(p), 'rb')
    # TODO: streaming
    body = stream.read()
    return web.Response(body=body, content_type=mimetypes.guess_type(fn)[0])


@app.GET('/pyq')
class SmolApp(Socket):
    async def on_load(self):
        await self('a[href="#packs"]').tab('show')
        # TODO: Load packlist
