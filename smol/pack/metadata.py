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

import abc.collections
import aiofiles
import yaml
import logging
import abc


class Service(abc.collections.Mapping):
    def __init__(self):
        self._data = {}

    async def load(self, path):
        self._path = path

        # TODO: Stream
        async with aiofiles.open(path) as db:
            data = await db.read()

        for pdata in yaml.safe_load_all(data):
            try:
                pd = DATA_TYPES[pdata](**pdata)
                self._data[pd.uri, pd.version] = pd
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
        if ver is ...:
            raise KeyError("Cowardly refusing to do wildcard deletes")
        
        del self._data[key]

    async def update_all(self):
        # Checks all source URLs, updates/adds pack metadata
        ...
        # If there's any packs that are not available and not installed, remove them.
        for uriver, data in self.items():
            if not data.available and data.installpath is None:
                del self[univer]

        await self.save()

    async def add_from_URL(self, url):
        # Download, determine if this is a pack or manifest
        ...
        await self.save()

    async def add_from_file(self, path):
        # Assume pack
        ...
        await self.save()


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
    uri = None
    directory = None
    platforms = []
    _metadata = None
    source = None
    version = None
    latest = None

    def __init__(self, **attrs):
        ...

    def yaml(self):
        ...
    
    def getpack(self):
        # Build pack object based on platforms in use.
        ...

    @abc.abstractmethod
    async def getstream(self):
        pass

    @abc.abstractmethod
    async def check_for_updates(self):
        pass


class ManifestPackData(AbstractPackData):
    ...


class UrlPackData(AbstractPackData):
    ...


class FilePackData(AbstractPackData):
    ...


DATA_TYPES = {
    'manifest': ManifestPackData,
    'url': UrlPackData,
    'file': FilePackData,
}
