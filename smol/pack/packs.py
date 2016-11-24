"""
Classes to deal with packs on the system: installation, starting, etc
"""


class BasePack:
    """
    Has no knowledge of minecraft or forge.
    """
    def __init__(self, metadata, stream):
        self.metadata = metadata
        self.getstream = stream

    async def install(self):
        ...

    async def run(self):
        raise NotImplementedError


class Minecraft(BasePack):
    """
    Handles Vanilla minecraft
    """
    async def install(self):
        ...

    async def run(self):
        ...


class Forge(BasePack):
    """
    Handles Forge-based modpacks
    """
    async def install(self):
        ...

    async def run(self):
        ...


def build_platform(names):
    TYPES = {
        'minecraft': Minecraft,
        'forge': Forge,
    }
    bases = tuple(*(TYPES[n] for n, _ in reversed(names)))
    name = ''.join(n for n, _ in names)
    return type(name, bases, {})
