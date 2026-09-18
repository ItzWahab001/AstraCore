from __future__ import annotations
from .db import db

# Schema creation is idempotent; migration records make future upgrades explicit.
MIGRATIONS={1:'initial-production-schema'}
async def apply_migrations():
    current=await db.fetchone('SELECT COALESCE(MAX(version),0) AS version FROM migrations')
    version=int(current['version']) if current else 0
    for number,description in sorted(MIGRATIONS.items()):
        if number>version:
            await db.execute('INSERT INTO migrations(version) VALUES(?)',(number,))
