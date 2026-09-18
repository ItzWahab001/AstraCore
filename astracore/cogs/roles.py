import discord,json
from discord import app_commands
from discord.ext import commands
from database.db import db
class Roles(commands.Cog):
 def __init__(self,bot):self.bot=bot
 @app_commands.command(name='role',description='Add or remove a self-assignable role.')
 async def role(self,i,role:discord.Role):
  cfg=await db.fetchone('SELECT roles FROM role_menus WHERE guild_id=? LIMIT 1',(i.guild.id,));allowed=set(json.loads(cfg['roles'])) if cfg else set()
  if role.id not in allowed:return await i.response.send_message('That role is not self-assignable.',ephemeral=True)
  if role in i.user.roles:await i.user.remove_roles(role,reason='AstraCore self role');await i.response.send_message(f'➖ Removed {role.mention}.',ephemeral=True)
  elif role < i.guild.me.top_role:await i.user.add_roles(role,reason='AstraCore self role');await i.response.send_message(f'➕ Added {role.mention}.',ephemeral=True)
  else:await i.response.send_message('Bot cannot manage that role.',ephemeral=True)
 @app_commands.command(name='role-menu-config',description='Configure comma-separated role IDs for self assignment.')
 @app_commands.checks.has_permissions(manage_roles=True)
 async def config(self,i,role_ids:str):
  try:ids=[int(x.strip()) for x in role_ids.split(',') if x.strip()];[i.guild.get_role(x) or (_ for _ in ()).throw(ValueError()) for x in ids]
  except ValueError:return await i.response.send_message('Every value must be an existing role ID.',ephemeral=True)
  await db.execute('INSERT INTO role_menus(guild_id,message_id,roles) VALUES(?,?,?) ON CONFLICT(message_id) DO UPDATE SET roles=excluded.roles',(i.guild.id,-i.guild.id,json.dumps(ids)));await i.response.send_message('🎭 Self-role list configured.',ephemeral=True)
async def setup(bot):await bot.add_cog(Roles(bot))
