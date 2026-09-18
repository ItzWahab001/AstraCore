import discord
from discord import app_commands
from discord.ext import commands
from views.panels import HelpView
class Core(commands.Cog):
    def __init__(self,bot):self.bot=bot
    @app_commands.command(name='help',description='Open the interactive AstraCore help panel.')
    async def help(self,i): await i.response.send_message(embed=discord.Embed(title='🚀 AstraCore',description='Select a category for commands and usage.',color=discord.Color.blurple()),view=HelpView(),ephemeral=True)
    @app_commands.command(name='ping',description='Show bot and WebSocket latency.')
    async def ping(self,i): await i.response.send_message(f'🏓 WebSocket: **{round(self.bot.latency*1000)}ms**',ephemeral=True)
    @app_commands.command(name='serverinfo',description='Show server information.')
    async def serverinfo(self,i):
        g=i.guild; e=discord.Embed(title=g.name,color=discord.Color.blurple());e.add_field(name='Members',value=str(g.member_count));e.add_field(name='Channels',value=str(len(g.channels)));e.add_field(name='Roles',value=str(len(g.roles)));e.add_field(name='Created',value=discord.utils.format_dt(g.created_at,'F'));await i.response.send_message(embed=e)
    @app_commands.command(name='userinfo',description='Show user information.')
    async def userinfo(self,i,user:discord.Member|None=None):
        u=user or i.user;e=discord.Embed(title=str(u),color=u.color);e.set_thumbnail(url=u.display_avatar.url);e.add_field(name='ID',value=str(u.id));e.add_field(name='Joined',value=discord.utils.format_dt(u.joined_at,'F') if u.joined_at else 'Unknown');e.add_field(name='Created',value=discord.utils.format_dt(u.created_at,'F'));await i.response.send_message(embed=e)
async def setup(bot):await bot.add_cog(Core(bot))
