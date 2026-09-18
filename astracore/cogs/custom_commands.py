import discord,time
from discord import app_commands
from discord.ext import commands
from database.db import db
from utils.core import rate
class CustomCommands(commands.Cog):
 def __init__(self,bot):self.bot=bot
 @app_commands.command(name='custom-create',description='Create a server custom command.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def create(self,i,name:str,response:str,cooldown:app_commands.Range[int,0,3600]=5):
  name=name.lower().strip()
  if not name.isidentifier() or len(name)>32:return await i.response.send_message('Command name must be 1-32 letters/numbers/underscore.',ephemeral=True)
  await db.execute('INSERT INTO custom_commands(guild_id,name,response,cooldown) VALUES(?,?,?,?) ON CONFLICT(guild_id,name) DO UPDATE SET response=excluded.response,cooldown=excluded.cooldown,enabled=1',(i.guild.id,name,response,cooldown));await i.response.send_message(f'✅ Custom command `/{name}` saved.',ephemeral=True)
 @app_commands.command(name='custom-delete',description='Delete a server custom command.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def delete(self,i,name:str):await db.execute('DELETE FROM custom_commands WHERE guild_id=? AND name=?',(i.guild.id,name.lower()));await i.response.send_message('🗑️ Custom command deleted.',ephemeral=True)
 @app_commands.command(name='custom-list',description='List server custom commands.')
 async def list_(self,i):rows=await db.fetchall('SELECT name,enabled,uses FROM custom_commands WHERE guild_id=? ORDER BY name',(i.guild.id,));d='\n'.join(f'`{r["name"]}` — {"enabled" if r["enabled"] else "disabled"} — {r["uses"]} uses' for r in rows) or 'No custom commands.';await i.response.send_message(d,ephemeral=True)
 @commands.Cog.listener()
 async def on_message(self,m):
  if m.author.bot or not m.guild or not m.content.startswith('/'):return
  name=m.content[1:].split()[0].lower();r=await db.fetchone('SELECT * FROM custom_commands WHERE guild_id=? AND name=? AND enabled=1',(m.guild.id,name))
  if not r:return
  if not rate.allow((m.guild.id,m.author.id,'cc',name),1,max(1,r['cooldown'])):return
  text=r['response'].replace('{user}',m.author.mention).replace('{username}',m.author.display_name).replace('{server}',m.guild.name)
  await db.execute('UPDATE custom_commands SET uses=uses+1 WHERE guild_id=? AND name=?',(m.guild.id,name));await m.channel.send(text[:2000],allowed_mentions=discord.AllowedMentions(users=True))
async def setup(bot):await bot.add_cog(CustomCommands(bot))
