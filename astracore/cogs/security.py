import time,discord
from collections import defaultdict,deque
from discord import app_commands
from discord.ext import commands
from services.config_service import get
from services.security_engine import security_engine, SecurityEvent
from database.db import db

class Security(commands.Cog):
 def __init__(self,bot):self.bot=bot;self.joins=defaultdict(deque)
 async def track(self,guild_id,actor_id,action,target_id=None):
  cfg=await get(guild_id);trusted=actor_id in {guild_id, getattr(self.bot.user,'id',0)}
  decision=security_engine.record(SecurityEvent(guild_id,actor_id,action,target_id,trusted=trusted))
  await db.execute('INSERT INTO security_events(guild_id,actor_id,action,target_id,risk,decision,reason) VALUES(?,?,?,?,?,?,?)',(guild_id,actor_id,action,target_id,decision.risk,decision.action,decision.reason))
  if decision.action=='lockdown' and cfg.get('auto_lockdown'):
   await self.apply_lockdown(self.bot.get_guild(guild_id),f'AstraCore Security 2.0: {decision.reason}')
  return decision
 async def apply_lockdown(self,guild,reason):
  if not guild:return 0
  ok=0
  for ch in guild.text_channels:
   try:await ch.set_permissions(guild.default_role,send_messages=False,reason=reason);ok+=1
   except (discord.Forbidden,discord.HTTPException):continue
  return ok
 @commands.Cog.listener()
 async def on_member_join(self,m):
  q=self.joins[m.guild.id];now=time.monotonic();q.append(now)
  while q and now-q[0]>60:q.popleft()
  cfg=await get(m.guild.id);threshold=int(cfg.get('raid_join_threshold',20))
  if len(q)>=threshold and cfg.get('auto_lockdown'):await self.apply_lockdown(m.guild,'AstraCore anti-raid threshold reached')
 @commands.Cog.listener()
 async def on_guild_channel_create(self,ch):
  if ch.guild.owner_id!=getattr(self.bot.user,'id',None): await self.track(ch.guild.id,ch.guild.owner_id,'channel_create',ch.id)
 @commands.Cog.listener()
 async def on_guild_channel_delete(self,ch):
  await self.track(ch.guild.id,ch.guild.owner_id,'channel_delete',ch.id)
 @commands.Cog.listener()
 async def on_guild_role_create(self,r):await self.track(r.guild.id,r.guild.owner_id,'role_create',r.id)
 @commands.Cog.listener()
 async def on_guild_role_delete(self,r):await self.track(r.guild.id,r.guild.owner_id,'role_delete',r.id)
 @app_commands.command(name='security',description='Show Security 2.0 status and recent risk events.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def security(self,i):
  c=await get(i.guild.id);rows=await db.fetchall('SELECT action,risk,decision,created_at FROM security_events WHERE guild_id=? ORDER BY id DESC LIMIT 5',(i.guild.id,));recent='\n'.join(f'• `{r["action"]}` risk `{r["risk"]}` → `{r["decision"]}`' for r in rows) or 'No correlated events yet.'
  await i.response.send_message(embed=discord.Embed(title='🛡️ Security 2.0',description=f'Auto-lockdown: `{c.get("auto_lockdown",False)}`\nJoin threshold: `{c.get("raid_join_threshold",20)}`\n\n**Recent events**\n{recent}'),ephemeral=True)
 @app_commands.command(name='lockdown',description='Emergency lockdown all text channels.')
 @app_commands.checks.has_permissions(administrator=True)
 async def lockdown(self,i):
  await i.response.defer(ephemeral=True);ok=await self.apply_lockdown(i.guild,f'Emergency lockdown by {i.user}');await i.followup.send(f'🔒 Locked {ok} text channels.',ephemeral=True)
 @app_commands.command(name='unlockdown',description='Remove emergency text-channel locks.')
 @app_commands.checks.has_permissions(administrator=True)
 async def unlockdown(self,i):
  await i.response.defer(ephemeral=True);ok=0
  for ch in i.guild.text_channels:
   try:await ch.set_permissions(i.guild.default_role,send_messages=None,reason=f'Lockdown removed by {i.user}');ok+=1
   except (discord.Forbidden,discord.HTTPException):continue
  await i.followup.send(f'🔓 Unlocked {ok} text channels.',ephemeral=True)
async def setup(bot):await bot.add_cog(Security(bot))
