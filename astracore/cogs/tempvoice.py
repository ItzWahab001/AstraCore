import discord
from discord import app_commands
from discord.ext import commands
from services.config_service import get,set_value
class TempVoice(commands.Cog):
 def __init__(self,bot):self.bot=bot;self.owners={}
 @app_commands.command(name='tempvoice-setup',description='Set a join-to-create voice channel.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def setup_cmd(self,i,channel:discord.VoiceChannel):await set_value(i.guild.id,'tempvoice_trigger_id',channel.id);await i.response.send_message('🔊 Temp voice trigger configured.',ephemeral=True)
 @commands.Cog.listener()
 async def on_voice_state_update(self,m,b,a):
  if a.channel and a.channel.id in self.owners and not a.channel.members:
   try:await a.channel.delete(reason='AstraCore temporary voice cleanup')
   except discord.HTTPException: return
  if not b.channel:return
  c=await get(m.guild.id);trigger=int(c.get('tempvoice_trigger_id',0))
  if b.channel.id!=trigger:return
  try:
   ch=await m.guild.create_voice_channel(f'{m.display_name} Room',category=b.channel.category,reason='AstraCore temporary voice')
   self.owners[ch.id]=m.id;await m.move_to(ch)
  except discord.HTTPException: return
 @app_commands.command(name='tempvoice-rename',description='Rename your temporary voice channel.')
 async def rename(self,i,name:str):
  if not i.user.voice or i.user.voice.channel.id not in self.owners or self.owners[i.user.voice.channel.id]!=i.user.id:return await i.response.send_message('You do not own this temporary channel.',ephemeral=True)
  await i.user.voice.channel.edit(name=name[:100]);await i.response.send_message('✅ Renamed.',ephemeral=True)
 @app_commands.command(name='tempvoice-limit',description='Set your temporary voice user limit.')
 async def limit(self,i,limit:app_commands.Range[int,0,99]):
  if not i.user.voice or i.user.voice.channel.id not in self.owners or self.owners[i.user.voice.channel.id]!=i.user.id:return await i.response.send_message('You do not own this temporary channel.',ephemeral=True)
  await i.user.voice.channel.edit(user_limit=limit);await i.response.send_message('✅ User limit updated.',ephemeral=True)
async def setup(bot):await bot.add_cog(TempVoice(bot))
