"""
Deals with downloading files nicely.
"""
import aiohttp
from .dirge import registry, inject

@registry.register
def http_session():
    # FIXME: Clean this up some how?
    return aiohttp.ClientSession()


class DownloadError(Exception):
    """
    Error downloading file
    """


@registry.register
class Downloader:
    session = inject('http_session')

    CHUNK_SIZE = 4 * 1024

    async def get(self, url, **kwargs):
        with (await self.session).get(url, **kwargs) as resp:
            if resp.status != 200:
                raise DownloadError(resp)
            yield await resp.read(self.CHUNK_SIZE)

    async def to_aiofile(self, target, url, **kwargs):
        async for chunk in self.get(url, **kwargs):
            await target.write(chunk)
