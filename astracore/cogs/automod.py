import re,time,discord
from collections import defaultdict
from discord.ext import commands
from services.config_service import get
class AutoMod(commands.Cog):
 def __init__(self,bot):self.bot=bot;self.last=defaultdict(list)
 @commands.Cog.listener()
 async def on_message(self,m):
  if m.author.bot or not m.guild:return
  c=await get(m.guild.id);cfg=c.get('automod',{})
  if not cfg.get('enabled',False):return
  if any(r.id in cfg.get('exempt_role_ids',[]) for r in getattr(m.author,'roles',[])):return
  reasons=[];txt=m.content
  words={x.lower() for x in cfg.get('bad_words',[])}
  if any(w and re.search(rf'\b{re.escape(w)}\b',txt,re.I) for w in words):reasons.append('blocked word')
  if len(m.mentions)>int(cfg.get('mention_limit',5)):reasons.append('mention spam')
  if 'discord.gg/' in txt.lower() and cfg.get('block_invites',True):reasons.append('invite link')
  if len(txt)>int(cfg.get('max_message_length',4000)):reasons.append('message too long')
  key=(m.guild.id,m.author.id);now=time.monotonic();hist=[t for t in self.last[key] if now-t<8];hist.append(now);self.last[key]=hist
  if len(hist)>=int(cfg.get('message_burst',8)):reasons.append('flood')
  if reasons:
   try:await m.delete(reason='AstraCore AutoMod: '+', '.join(reasons))
   except discord.HTTPException:return
   if cfg.get('warn_on_action',True):
    try:await m.channel.send(f'⚠️ {m.author.mention}, your message was removed by AutoMod: {", ".join(reasons)}.',delete_after=5)
    except discord.HTTPException: return
async def setup(bot):await bot.add_cog(AutoMod(bot))
