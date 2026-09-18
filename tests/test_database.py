import pytest
from pathlib import Path
@pytest.mark.asyncio
async def test_database_initializes(tmp_path,monkeypatch):
    import database.db as mod
    monkeypatch.setattr(mod,'DB_PATH',str(tmp_path/'test.db'))
    mod.db.path=mod.DB_PATH
    await mod.db.init()
    assert Path(mod.DB_PATH).exists()
    row=await mod.db.fetchone("SELECT name FROM sqlite_master WHERE type='table' AND name='guild_settings'")
    assert row is not None
