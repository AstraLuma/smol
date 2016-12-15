import pytest

from smol.dirge import AsyncInit, _Registry
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


@pytest.mark.asyncio
async def test_factory():
    reg = _Registry()

    @reg.register
    def spam():
        return "eggs"

    aw = reg['spam']
    assert inspect.isawaitable(aw)
    inst = await aw
    assert inst == 'eggs'


@pytest.mark.asyncio
async def test_async_factory():
    reg = _Registry()

    @reg.register
    async def spam():
        return "eggs"

    aw = reg['spam']
    assert inspect.isawaitable(aw)
    inst = await aw
    assert inst == 'eggs'


@pytest.mark.asyncio
async def test_reg_type():
    reg = _Registry()

    @reg.register
    class Spam:
        pass

    aw = reg['Spam']
    assert inspect.isawaitable(aw)
    inst = await aw
    assert isinstance(inst, Spam)


@pytest.mark.asyncio
async def test_async_type():
    reg = _Registry()

    @reg.register
    class Spam(metaclass=AsyncInit):
        async def __ainit__(self):
            pass

    aw = reg['Spam']
    assert inspect.isawaitable(aw)
    inst = await aw
    assert isinstance(inst, Spam)


@pytest.mark.asyncio
async def test_multi():
    reg = _Registry()

    @reg.register
    class Spam:
        pass

    thing1 = await reg['Spam']
    thing2 = await reg['Spam']
    assert thing1 is thing2
