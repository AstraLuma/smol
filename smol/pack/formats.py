"""
Helpers just to parse the data formats.
"""
import yaml
import zipfile
import io
import collections.abc
import aiohttp


class Version(str):
    __slots__ = '_tuple'

    @property
    def tuple(self):
        if not hasattr(self, '_tuple'):
            self._tuple = tuple(map(int, self.split('.')))
        return self._tuple

    def __eq__(self, other):
        if isinstance(other, str):
            other = Version(other)
        if isinstance(other, tuple):
            return self.tuple == other
        else:
            return self.tuple == other.tuple



def yaml_map_list(seq):
    """
    Takes a YAML ordered map and yields a sequence of tuples
    """
    return [next(iter(i.items())) for i in seq]


class SmolPack(collections.abc.Mapping):
    @classmethod
    def from_buffer(cls, data):
        zf = zipfile.ZipFile(io.BytesIO(data))
        return SmolPack(zf)

    def __init__(self, zf):
        self._md = {}
        with zf.open('smoldata.yaml') as sdy:
            self._init_metadata(sdy.read())
        self._zf = zf

    def _init_metadata(self, buf):
        data = yaml.safe_load(buf)
        self._files = data.pop('files')
        self._md['platforms'] = list(yaml_map_list(data.pop('platforms')))
        self._md.update(data)
        if 'version' in self._md:
            self._md['version'] = Version(self._md['version'])

    def __getitem__(self, key):
        return self._md[key]

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    async def read_bytes(self, filename):
        if filename in self._files:
            async with aiohttp.ClientSession() as session:
                async with session.get(self._files[filename]['url']) as response:
                    return await response.read()
        else:
            return self._zf.read(filename)

    async def read_string(self, filename, encoding='utf-8'):
        return (await self.read_bytes(filename)).decode(encoding)


class ManifestItem:
    @classmethod
    def from_dict(cls, data):
        self = cls()
        data = data.copy()

        self.id = data.pop('id')
        self.url = data.pop('url')
        self.version = data.pop('version')
        self.platforms = list(yaml_map_list(data.pop('platforms')))
        self.name = data.pop('name', self.id)
        self.description = data.pop('description', None)

        self.extras = data

        return self


class SmolManifest(collections.abc.Sequence):
    def __init__(self):
        self._packages = []

    @classmethod
    def from_buffer(cls, buffer):
        self = SmolManifest()

        for pdata in yaml.safe_load_all(buffer):
            self._packages.append(ManifestItem.from_dict(pdata))

        return self

    def __getitem__(self, key):
        return self._packages[key]

    def __len__(self):
        return len(self._packages)
