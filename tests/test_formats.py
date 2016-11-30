import pytest
import pathlib

from smol.pack.formats import SmolPack


@pytest.fixture(scope="session")
def pack_buffer():
    fn = pathlib.Path(__file__).parent / "test.smolpack"
    return fn.read_bytes()


def test_metadata(pack_buffer):
    pack = SmolPack.from_buffer(pack_buffer)
    assert pack['id'] == 'testpack'
    assert pack['name'] == 'Test Pack'
    assert pack['description'].strip() == 'baz\nquux'
    assert pack['version'] == '1.0'
    assert pack['platforms'] == [('minecraft', '1.10.0')]
    assert 'files' not in pack


@pytest.mark.asyncio
async def test_bundled_file(pack_buffer):
    pack = SmolPack.from_buffer(pack_buffer)
    assert (await pack.read_string('foo')).strip() == 'bar'


@pytest.mark.asyncio
async def test_remote_file(pack_buffer):
    pack = SmolPack.from_buffer(pack_buffer)
    assert (await pack.read_string('spam')).strip() == 'eggs'
