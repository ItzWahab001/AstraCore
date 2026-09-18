import discord
from discord.ext import commands
from services.config_service import get
class Welcome(commands.Cog):
 def __init__(self,bot):self.bot=bot
 async def send(self,m,event):
  c=await get(m.guild.id);cfg=c.get(event,{})
  if not cfg.get('enabled'):return
  ch=m.guild.get_channel(int(cfg.get('channel_id',0)))
  if not ch:return
  text=cfg.get('message','{mention} welcome to {server}!').format(mention=m.mention,user=m.display_name,server=m.guild.name,count=m.guild.member_count)
  try:await ch.send(text)
  except discord.HTTPException: return
 @commands.Cog.listener()
 async def on_member_join(self,m):await self.send(m,'welcome')
 @commands.Cog.listener()
 async def on_member_remove(self,m):await self.send(m,'goodbye')
async def setup(bot):await bot.add_cog(Welcome(bot))
