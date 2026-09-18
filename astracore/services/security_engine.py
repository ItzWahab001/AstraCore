from __future__ import annotations
import time
from dataclasses import dataclass, field
from collections import defaultdict, deque
from typing import Iterable

@dataclass(frozen=True)
class SecurityEvent:
    guild_id:int; actor_id:int; action:str; target_id:int|None=None; timestamp:float=field(default_factory=time.monotonic); trusted:bool=False

@dataclass(frozen=True)
class SecurityDecision:
    risk:int; action:str; reason:str

class SecurityEngine:
    """In-memory event correlation engine; persistence is handled by the database/audit cog."""
    def __init__(self): self._events=defaultdict(deque); self._exempt=defaultdict(set)
    def exempt(self,guild_id:int,*user_ids:int)->None: self._exempt[guild_id].update(user_ids)
    def revoke_exemption(self,guild_id:int,*user_ids:int)->None:
        for uid in user_ids:self._exempt[guild_id].discard(uid)
    def record(self,event:SecurityEvent,window:float=60)->SecurityDecision:
        if event.actor_id in self._exempt[event.guild_id] or event.trusted:return SecurityDecision(0,'allow','exempt/trusted actor')
        q=self._events[(event.guild_id,event.actor_id)]; now=event.timestamp; q.append(event)
        while q and now-q[0].timestamp>window:q.popleft()
        counts=defaultdict(int)
        for e in q:counts[e.action]+=1
        total=sum(counts.values()); distinct=len(counts)
        risk=min(100, total*8 + max(0,distinct-1)*10)
        if risk>=80:return SecurityDecision(risk,'lockdown','high-confidence correlated activity')
        if risk>=50:return SecurityDecision(risk,'alert','suspicious correlated activity')
        return SecurityDecision(risk,'log','normal activity')
    def recent(self,guild_id:int,actor_id:int,limit:int=20):return list(self._events[(guild_id,actor_id)])[-limit:]

security_engine=SecurityEngine()
