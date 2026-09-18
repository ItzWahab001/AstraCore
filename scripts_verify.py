"""Offline production verification: AST parsing, feature registry, and pure service checks."""
from pathlib import Path
import ast, asyncio
from astracore.features import FEATURES, FEATURE_COUNT
from astracore.services.cache import TTLCache
from astracore.services.rate_limit import SlidingWindowLimiter
from astracore.services.security_engine import SecurityEngine, SecurityEvent
root=Path(__file__).parent
for p in root.rglob('*.py'):
    if '__pycache__' not in p.parts: ast.parse(p.read_text(encoding='utf-8'))
assert FEATURE_COUNT>=500 and len(FEATURES)==FEATURE_COUNT
async def main():
    c=TTLCache(ttl=5); await c.set('k','v'); assert await c.get('k')=='v'
    l=SlidingWindowLimiter(); assert (await l.check('verify',1,10))[0]; assert not (await l.check('verify',1,10))[0]
asyncio.run(main())
e=SecurityEngine();
for _ in range(12): d=e.record(SecurityEvent(1,2,'channel_delete'))
assert d.action=='lockdown'
print(f'OFFLINE_VERIFY_OK feature_count={FEATURE_COUNT}')
