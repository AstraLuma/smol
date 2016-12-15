"""
The pack metadata service. Stores metadata and handles querying for updates.
"""

# There are 4 types of packs:
# * Packs from manifests
# * Packs from direct URLs
# * Packs from files
# * Virtual Packs
#
# Manifest packs are the nicest. We can just grab the manifest on a "schedule"
# and update the upstram pack metadata from that. We also have the potential for
# multiple versions being available.
#
# Direct URL packs we have to use HTTP caching mechanisms (ETag, Last-Modified),
# in order to detect updates. If we want old versions, we have to keep them on 
# disk.
#
# File packs are just hopeless. No features at all.
#
# Virtual packs have no concrete pack files, but instead are base platform packs,
# ie Vanilla (Beta, Alpha), Forge, etc.


# Thinking pack objects are mostly about the platform they're based on, not the source they came from.
# The metadata comes from the source. Metadata pass the Pack object a factory for the data stream and the metadata.
# The Pack is concerned with how to install and start. The metadata deals with updates and such.

import collections.abc
import abc
import logging
import asyncio
import aiofiles
import yaml
import yurl

from .packs import build_platform
from ..downloader import Downloader
from ..dirge import inject, registry


@registry.register("pack_metadata")
class Service(collections.abc.Mapping):
    dler = inject(Downloader)

    def __init__(self):
        self._data = {}

    async def load(self, path):
        self._path = path

        # TODO: Stream
        async with aiofiles.open(path) as db:
            data = await db.read()

        for pdata in yaml.safe_load_all(data):
            try:
                self._add_from_dict(pdata)
            except Exception:
                logging.getLogger('smol.pack.metadata').exception("Unable to load pack data for %r", pdata)


    async def save(self, path=None):
        if path is None:
            path = self._path
        # TODO: Stream
        buf = yaml.safe_dump_all(pd.yaml() for pd in self._data.values())
        async with aiofiles.open(path, 'w') as db:
            await db.write(buf)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            uri, ver = key
        else:
            uri, ver = key, ...

        if ver is ...:
            return [pack for pack in self._data.values() if pack.uri == uri]
        else:
            return self._data[uri, ver]

    def __len__(self):
        # Counts the individual pack versions
        return len(self._data)

    def __iter__(self):
        # Yields the (uri, version) pairs
        yield from self._data

    def __contains__(self, key):
        if isinstance(key, tuple):
            uri, ver = key
        else:
            uri, ver = key, ...

        if ver is ...:
            return any(True for u, v in self._data.keys() if u == uri)
        else:
            return (uri, ver) in self._data

    def __delitem__(self, key):
        if not isinstance(key, tuple) or key[1] is ...:
            raise KeyError("Cowardly refusing to do wildcard deletes")
        
        del self._data[key]

    async def update_all(self):
        # Checks all source URLs, updates/adds pack metadata
        await asyncio.gather(
            *(pd.check_for_updates() for pd in self.values())
        )
        # If there's any packs that are not available and not installed, remove them.
        for uriver, data in self.items():
            if not data.available and data.installpath is None:
                del self[univer]

        await self.save()

    async def add_from_URL(self, url):
        # Download, determine if this is a pack or manifest
        buf = await (await self.dler).get(url)
        try:
            # Try as YAML: is manifest
            for pdata in yaml.safe_load_all(buf):
                try:
                    self._add_from_dict(pdata)
                except Exception:
                    logging.getLogger('smol.pack.metadata').exception("Unable to load pack data for %r", pdata)
        except Exception:
            # Try as zip: is smolpack
            await self._add_from_pack(buf)

        await self.save()

    async def add_from_file(self, path):
        # Assume pack
        async with aiofiles.open(path, 'rb') as pack:
            buf = await pack.read()

        await self._add_from_pack(buf)

        await self.save()

    async def _add_from_pack(self, buf):
        ...

    async def _add_from_dict(self, pdata):
        pd = DATA_TYPES[pdata](**pdata)
        self._data[pd.uri, pd.version] = pd


# Schema: 
# Canonical fields: type, uri, version, source, installpath, available (is the source URL still valid?)
# Cached (from pack): platforms, extras
# Calculated: latest
#
# Available depends on source:
# * URL: Is the URL not 404 or 410?
# * Manifest: Is the manifest not 404 or 410 and is the pack/version still in the manifest?
# * File: True (pack is copied to application directory first, and thus is always available)


class AbstractPackData(abc.ABC):
    id = None
    url = None
    version = None
    platforms = []
    name = None
    description = None
    extras = {}
    directory = None
    _metadata = None
    source = None
    latest = None

    def __init__(self, serv, **attrs):
        self._serv = serv
        self.platforms = []
        self.extras = {}
        for k, v in attrs.items():
            if hasattr(type(self), k):
                setattr(self, k, v)

    @classmethod
    def from_item(cls, serv, item):
        return cls(serv, **vars(item))

    def getpack(self):
        # Build pack object based on platforms in use.
        return build_platform(self.platforms.keys())(self, self.getstream)

    @abc.abstractmethod
    async def getstream(self):
        """
        Returns an async iterable returning chunks of data.

        This data is not guarenteed to be a particular size, by line, or anything.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def check_for_updates(self):
        """
        Calls out to wherever and sees if there's a new version of the pack.

        If so, it'll be added to the metadata service.
        """
        raise NotImplementedError


class ManifestPackData(AbstractPackData):
    _dl = inject(Downloader)

    async def getstream(self):
        ...

    _requests = {}

    @staticmethod
    async def _real_update( url):
        buf = await (await self._dl).get(url)
        manifest = yaml.safe_load_all(buf)

        for pack in manifest:
            uriver = pack['uri'], pack['version']
            if uriver in self._serv:
                self._serv[uriver]._update_from_dict(pack)
            else:
                self._serv._add_from_dict(pack)

    async def check_for_updates(self):
        mani = str(yurl.URL(self.source).replace(fragment=None))
        if mani not in self._requests:
            self._requests[mani] = asyncio.ensure_future(_real_update(mani))

        await self._requests[mani]


class UrlPackData(AbstractPackData):
    ...
    # TODO: HTTP caching
    # TODO: Update/version magic?


class FilePackData(AbstractPackData):
    ...


DATA_TYPES = {
    'manifest': ManifestPackData,
    'url': UrlPackData,
    'file': FilePackData,
}
