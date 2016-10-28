from pyquery import PyQueryApp, errors

class SmolApp(PyQueryApp):
    async def on_load(self):
        await self('#packs').tab('show')
