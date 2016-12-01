import pytest
from smol.pack.packs import BasePack


@pytest.mark.asyncio
async def test_install(tmpdir, smolpack):
    async def loadpack():
        return smolpack
    p = BasePack(str(tmpdir), loadpack)
    await p.install()

    assert (tmpdir / 'foo').read_text('utf-8').strip() == 'bar'
    assert (tmpdir / 'spam').read_text('utf-8').strip() == 'eggs'
