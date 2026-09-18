from __future__ import annotations
import asyncio, time
from collections import defaultdict, deque

class RateLimitExceeded(Exception):
    def __init__(self, retry_after: float): self.retry_after = retry_after; super().__init__(f"Retry after {retry_after:.1f}s")

class SlidingWindowLimiter:
    def __init__(self): self._windows=defaultdict(deque); self._lock=asyncio.Lock()
    async def check(self, key: str, limit: int, window: float) -> tuple[bool,float]:
        now=time.monotonic()
        async with self._lock:
            q=self._windows[key]
            while q and now-q[0]>=window:q.popleft()
            if len(q)>=limit:return False,max(0.0,window-(now-q[0]))
            q.append(now);return True,0.0
    async def enforce(self,key,limit,window):
        ok,retry=await self.check(key,limit,window)
        if not ok:raise RateLimitExceeded(retry)

limiter=SlidingWindowLimiter()
