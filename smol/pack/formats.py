"""
Helpers just to parse the data formats.
"""
import yaml
import collections.abc


class SmolPack:
    ...


def yaml_map_list(seq):
    """
    Takes a YAML ordered map and yields a sequence of tuples
    """
    return map(next, seq.items())

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
