import asyncio
from services.cache import TTLCache
from services.rate_limit import SlidingWindowLimiter

def test_cache_and_rate_limit():
    async def run():
        c=TTLCache(ttl=10);await c.set('x',42);assert await c.get('x')==42;await c.delete('x');assert await c.get('x') is None
        l=SlidingWindowLimiter();assert (await l.check('k',1,60))[0] is True;assert (await l.check('k',1,60))[0] is False
    asyncio.run(run())
