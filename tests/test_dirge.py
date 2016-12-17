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

    assert len(reg) == 1

    aw = reg['spam']
    assert len(reg) == 1
    assert inspect.isawaitable(aw)
    inst = await aw
    assert inst == 'eggs'


@pytest.mark.asyncio
async def test_async_factory():
    reg = _Registry()

    @reg.register
    async def spam():
        return "eggs"

    assert len(reg) == 1

    aw = reg['spam']
    assert len(reg) == 1
    assert inspect.isawaitable(aw)
    inst = await aw
    assert inst == 'eggs'


@pytest.mark.asyncio
async def test_reg_type():
    reg = _Registry()

    @reg.register
    class Spam:
        pass

    assert len(reg) == 1

    aw = reg['Spam']
    assert len(reg) == 1
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

    assert len(reg) == 1

    aw = reg['Spam']
    assert len(reg) == 1
    assert inspect.isawaitable(aw)
    inst = await aw
    assert isinstance(inst, Spam)


@pytest.mark.asyncio
async def test_multi():
    reg = _Registry()

    @reg.register
    class Spam:
        pass

    assert len(reg) == 1

    thing1 = await reg['Spam']
    thing2 = await reg['Spam']
    assert len(reg) == 1
    assert thing1 is thing2


@pytest.mark.asyncio
async def test_set():
    reg = _Registry()

    thing = object()

    reg['spam'] = thing

    assert len(reg) == 1

    aw = reg['spam']
    assert len(reg) == 1
    assert inspect.isawaitable(aw)
    inst = await aw
    assert inst is thing

@pytest.mark.asyncio
async def test_del():
    reg = _Registry()

    @reg.register
    class Spam:
        pass

    assert len(reg) == 1

    thing1 = await reg['Spam']

    assert len(reg) == 1
    del reg['Spam']
    assert len(reg) == 1

    thing2 = await reg['Spam']
    assert len(reg) == 1

    assert thing1 is not thing2


@pytest.mark.asyncio
async def test_wrap():
    reg = _Registry()

    @reg.register
    def spam():
        return "spam"

    @reg.wrap('spam')
    def wrap(obj):
        return obj+"eggs"

    assert len(reg) == 1

    inst = await reg['spam']
    assert inst == 'spameggs'


@pytest.mark.asyncio
async def test_async_wrap():
    reg = _Registry()

    @reg.register
    async def spam():
        return "spam"

    @reg.wrap('spam')
    async def wrap(obj):
        return obj+"eggs"

    assert len(reg) == 1

    inst = await reg['spam']
    assert inst == 'spameggs'

# TODO: Test inject.