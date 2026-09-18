from __future__ import annotations
import discord, logging, functools, time
from collections import defaultdict, deque
log=logging.getLogger('AstraCore')

class RateLimiter:
    def __init__(self): self.buckets=defaultdict(deque)
    def allow(self,key,limit,window):
        now=time.monotonic(); q=self.buckets[key]
        while q and now-q[0]>=window: q.popleft()
        if len(q)>=limit:return False
        q.append(now);return True
rate=RateLimiter()

def em(title, desc='', color=discord.Color.blurple()): return discord.Embed(title=title,description=desc,color=color,timestamp=discord.utils.utcnow())
def ok(t,d=''): return em('✅ '+t,d,discord.Color.green())
def err(t,d=''): return em('❌ '+t,d,discord.Color.red())
def info(t,d=''): return em('ℹ️ '+t,d)
async def safe_send(interaction, content=None, embed=None, ephemeral=False, **kwargs):
    if interaction.response.is_done(): return await interaction.followup.send(content=content,embed=embed,ephemeral=ephemeral,**kwargs)
    return await interaction.response.send_message(content=content,embed=embed,ephemeral=ephemeral,**kwargs)

def bot_can_manage(guild, member, action='manage_roles'):
    me=guild.me
    return bool(me and getattr(me.guild_permissions,action,False)) and (not isinstance(member,discord.Member) or member.top_role < me.top_role)
