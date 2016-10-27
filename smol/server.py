from aiohttp import web
import pkg_resources
import pathlib
import mimetypes
import aiohttp_jinja2


@aiohttp_jinja2.template('index.html')
async def index(request):
    return {}

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

def setup_routes(app):
    app.router.add_get('/static/{filename}', static)
    app.router.add_get('/', index)
