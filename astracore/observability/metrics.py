from __future__ import annotations
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from threading import Lock

@dataclass
class Metrics:
    commands: Counter = field(default_factory=Counter)
    errors: Counter = field(default_factory=Counter)
    events: Counter = field(default_factory=Counter)
    timings: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
    _lock: Lock = field(default_factory=Lock, repr=False)

    def inc(self, name: str, value: int = 1, labels: tuple[str, ...] = ()) -> None:
        key = name if not labels else f"{name}|{'|'.join(labels)}"
        with self._lock: self.events[key] += value

    def observe(self, name: str, seconds: float) -> None:
        with self._lock:
            values = self.timings[name]
            values.append(max(0.0, seconds))
            if len(values) > 5000: del values[:len(values)-5000]

    def timer(self, name: str):
        metrics = self
        class _Timer:
            def __enter__(self): self.started = time.perf_counter(); return self
            def __exit__(self, *_): metrics.observe(name, time.perf_counter()-self.started)
        return _Timer()

    def snapshot(self) -> dict:
        with self._lock:
            result = {"events": dict(self.events), "commands": dict(self.commands), "errors": dict(self.errors)}
            result["timings"] = {k: {"count": len(v), "avg_ms": round(sum(v)/len(v)*1000, 2), "max_ms": round(max(v)*1000, 2)} for k,v in self.timings.items() if v}
            return result

metrics = Metrics()
