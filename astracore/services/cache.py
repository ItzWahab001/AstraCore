from __future__ import annotations
import asyncio, time
from dataclasses import dataclass
from typing import Any

@dataclass
class CacheItem:
    value: Any
    expires_at: float

class TTLCache:
    def __init__(self, ttl: float = 60.0, max_size: int = 5000):
        self.ttl, self.max_size = ttl, max_size; self._data: dict[str, CacheItem] = {}; self._lock = asyncio.Lock()
    async def get(self, key: str, default=None):
        async with self._lock:
            item = self._data.get(key)
            if not item: return default
            if item.expires_at <= time.monotonic(): self._data.pop(key, None); return default
            return item.value
    async def set(self, key: str, value: Any, ttl: float | None = None):
        async with self._lock:
            if len(self._data) >= self.max_size and key not in self._data:
                oldest = min(self._data, key=lambda k: self._data[k].expires_at); self._data.pop(oldest, None)
            self._data[key] = CacheItem(value, time.monotonic() + (self.ttl if ttl is None else ttl)); return value
    async def delete(self, key: str):
        async with self._lock: return self._data.pop(key, None) is not None
    async def clear(self):
        async with self._lock: self._data.clear()
    async def get_or_set(self, key, factory, ttl=None):
        value = await self.get(key)
        if value is not None: return value
        value = await factory(); await self.set(key, value, ttl); return value

config_cache = TTLCache(ttl=30, max_size=10000)
