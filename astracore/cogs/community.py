import discord,datetime
from discord import app_commands
from discord.ext import commands
from database.db import db
from services.config_service import get,set_value
class Community(commands.Cog):
 def __init__(self,bot):self.bot=bot
 @app_commands.command(name='suggest',description='Submit a server suggestion.')
 async def suggest(self,i,text:str):
  c=await get(i.guild.id);cid=int(c.get('suggestion_channel_id',0));ch=i.guild.get_channel(cid) if cid else i.channel
  if not ch:return await i.response.send_message('Suggestion channel is not configured.',ephemeral=True)
  await i.response.defer(ephemeral=True);m=await ch.send(embed=discord.Embed(title='💡 Suggestion',description=text).set_footer(text=f'Author ID: {i.user.id}'));await m.add_reaction('👍');await m.add_reaction('👎');await db.execute('INSERT INTO suggestions(guild_id,channel_id,message_id,author_id,text) VALUES(?,?,?,?,?)',(i.guild.id,ch.id,m.id,i.user.id,text));await i.followup.send(f'Suggestion posted: {m.jump_url}',ephemeral=True)
 @app_commands.command(name='suggestion-status',description='Set a suggestion status.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def suggestion_status(self,i,message_id:int,status:str):
  if status not in {'pending','approved','denied','considered'}:return await i.response.send_message('Status must be pending, approved, denied, or considered.',ephemeral=True)
  await db.execute('UPDATE suggestions SET status=? WHERE guild_id=? AND message_id=?',(status,i.guild.id,message_id));await i.response.send_message(f'💡 Status set to **{status}**.',ephemeral=True)
 @app_commands.command(name='starboard-set',description='Configure starboard channel and threshold.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def starboard_set(self,i,channel:discord.TextChannel,threshold:app_commands.Range[int,1,100]):await set_value(i.guild.id,'starboard_channel_id',channel.id);await set_value(i.guild.id,'star_threshold',threshold);await i.response.send_message('⭐ Starboard configured.',ephemeral=True)
 @commands.Cog.listener()
 async def on_raw_reaction_add(self,p):
  if str(p.emoji)!='⭐':return
  c=await get(p.guild_id);cid=int(c.get('starboard_channel_id',0));threshold=int(c.get('star_threshold',3));ch=self.bot.get_channel(cid) if cid else None
  if not ch:return
  source=self.bot.get_channel(p.channel_id)
  if not source:return
  try:m=await source.fetch_message(p.message_id)
  except discord.HTTPException:return
  reaction=next((x for x in m.reactions if str(x.emoji)=='⭐'),None)
  if not reaction or reaction.count<threshold:return
  old=await db.fetchone('SELECT starboard_message_id FROM starboard WHERE message_id=?',(m.id,))
  content=f'⭐ **{reaction.count}** {m.author.mention}\n{m.content[:1500]}\n[Jump to message]({m.jump_url})'
  try:
   if old:sm=await ch.fetch_message(old['starboard_message_id']);await sm.edit(content=content)
   else:sm=await ch.send(content);await db.execute('INSERT INTO starboard(message_id,guild_id,stars,starboard_message_id) VALUES(?,?,?,?)',(m.id,p.guild_id,reaction.count,sm.id))
  except discord.HTTPException: return
async def setup(bot):await bot.add_cog(Community(bot))
