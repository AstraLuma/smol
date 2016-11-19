"""
Classes to deal with packs on the system: installation, starting, etc
"""

class BasePack:
    """
    Has no knowledge of minecraft or forge.
    """
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
