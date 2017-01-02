import pytest
import pathlib

from smol.pack.formats import SmolPack


@pytest.fixture(scope="session")
def pack_buffer():
    fn = pathlib.Path(__file__).parent / "test.smolpack"
    return fn.read_bytes()


@pytest.fixture()
def smolpack(pack_buffer):
    return SmolPack.from_buffer(pack_buffer)
