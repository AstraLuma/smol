import pytest
from smol.pack.formats import Version


def test_metadata(smolpack):
    assert smolpack['id'] == 'testpack'
    assert smolpack['name'] == 'Test Pack'
    assert smolpack['description'].strip() == 'baz\nquux'
    assert smolpack['version'] == '1.0'
    assert smolpack['platforms'] == [('minecraft', '1.10.0')]
    assert 'files' not in smolpack


def test_metadata_version(smolpack):
    assert smolpack['version'].tuple == (1, 0)


@pytest.mark.asyncio
async def test_bundled_file(smolpack):
    assert (await smolpack.read_string('foo')).strip() == 'bar'


@pytest.mark.asyncio
async def test_remote_file(smolpack):
    assert (await smolpack.read_string('spam')).strip() == 'eggs'


def test_version_eq():
    assert Version('1.0') == '1.0'
    assert Version('1.0') == '1.00'
    assert Version('1.0') == (1, 0)
    assert Version('1.1') == Version('1.01')
    assert Version('1.0') != Version('1.0.0')
    assert Version('1.0') == Version('1.00')
