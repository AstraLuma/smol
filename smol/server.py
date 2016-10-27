from aiohttp import web


async def index(request):
    return web.Response(text='Hello Aiohttp!')

def setup_routes(app, project_root):
    app.router.add_get('/', index)

