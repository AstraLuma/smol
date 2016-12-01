"""
Classes to deal with packs on the system: installation, starting, etc
"""
import pathlib
import aiofiles

class BasePack:
    """
    Has no knowledge of minecraft or forge.
    """
    def __init__(self, base, loadfile):
        self.base = pathlib.Path(base)
        self.loadfile = loadfile

    async def install(self):
        sp = await self.loadfile()
        for fn in sp.files():
            buf = await sp.read_bytes(fn)
            async with aiofiles.open(str(self.base / fn), mode='wb') as f:
                await f.write(buf)

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
