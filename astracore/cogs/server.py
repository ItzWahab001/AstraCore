import discord
from discord import app_commands
from discord.ext import commands
class Server(commands.Cog):
 def __init__(self,bot):self.bot=bot
 @app_commands.command(name='channels',description='List server channels by type.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def channels(self,i):
  cats={'text':sum(isinstance(c,discord.TextChannel) for c in i.guild.channels),'voice':sum(isinstance(c,discord.VoiceChannel) for c in i.guild.channels),'category':sum(isinstance(c,discord.CategoryChannel) for c in i.guild.channels)};await i.response.send_message('📊 '+', '.join(f'{k}: **{v}**' for k,v in cats.items()),ephemeral=True)
 @app_commands.command(name='roles',description='List server roles.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def roles(self,i):await i.response.send_message('🎭 '+', '.join(r.mention for r in i.guild.roles[-50:]),ephemeral=True)
 @app_commands.command(name='permissions',description='Show your effective guild permissions.')
 async def permissions(self,i):p=i.user.guild_permissions;names=[n.replace('_',' ') for n,v in p if v];await i.response.send_message('🔐 '+', '.join(names)[:3900],ephemeral=True)
async def setup(bot):await bot.add_cog(Server(bot))
