import discord
from discord import app_commands
from discord.ext import commands
from views.premium_panels import PremiumDashboard
class Dashboard(commands.Cog):
    def __init__(self,bot):self.bot=bot
    @app_commands.command(name='dashboard',description='Open AstraCore premium control center.')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def dashboard(self,i):
        view=PremiumDashboard(self.bot,i.guild.id)
        await i.response.send_message(embed=discord.Embed(title='✨ AstraCore Premium Control Center',description='Select a system to inspect and control its live configuration.'),view=view,ephemeral=True)
async def setup(bot):await bot.add_cog(Dashboard(bot))
