import pytest

from smol.dirge import AsyncInit
import inspect

@pytest.mark.asyncio
async def test_asyncinit():
    class Spam(metaclass=AsyncInit):
        async def __ainit__(self):
            self.eggs = "sausage"

    aw = Spam()
    assert inspect.isawaitable(aw)
    inst = await aw
    assert inst.eggs == "sausage"
