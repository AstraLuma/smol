from .pyquery import PyQueryApp, errors

class SmolApp(PyQueryApp):
    async def on_load(self):
        await self('a[href="#packs"]').tab('show')
        # TODO: Load packlist