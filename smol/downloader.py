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

    async def get(self, url, **kwargs):
        # FIXME: Is there a better way to do this?
        with (await self.session).get(url, **kwargs) as resp:
            if resp.status != 200:
                raise DownloadError(resp)
            return await resp.read()
