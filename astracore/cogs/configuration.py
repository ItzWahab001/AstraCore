import discord
from discord import app_commands
from discord.ext import commands
from services.config_service import get,set_value
class Config(commands.Cog):
 def __init__(self,bot):self.bot=bot
 @app_commands.command(name='config',description='View server configuration.')
 @app_commands.checks.has_permissions(administrator=True)
 async def config(self,i):d=await get(i.guild.id);text='\n'.join(f'`{k}` = `{v}`' for k,v in d.items()) or 'No custom settings yet.';await i.response.send_message(embed=discord.Embed(title='⚙️ AstraCore Configuration',description=text),ephemeral=True)
 @app_commands.command(name='config-set',description='Set a supported server configuration key.')
 @app_commands.checks.has_permissions(administrator=True)
 async def set(self,i,key:str,value:str):
  allowed={'welcome_channel_id','log_channel_id','verification_channel_id','verified_role_id','unverified_role_id','ticket_category_id','staff_role_id','starboard_channel_id','star_threshold','suggestion_channel_id','leveling_enabled','economy_enabled','automod_enabled'}
  if key not in allowed:return await i.response.send_message('Unsupported configuration key.',ephemeral=True)
  parsed=int(value) if key.endswith('_id') or key in {'star_threshold'} else value.lower() if key.endswith('_enabled') else value
  await set_value(i.guild.id,key,parsed);await i.response.send_message(f'✅ `{key}` updated.',ephemeral=True)
async def setup(bot):await bot.add_cog(Config(bot))
