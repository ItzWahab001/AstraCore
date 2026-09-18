import discord, json
from discord import app_commands
from discord.ext import commands
from features import FEATURE_COUNT
from observability.metrics import metrics
from database.db import db
class Platform(commands.Cog):
 def __init__(self,bot):self.bot=bot
 @app_commands.command(name='feature-count',description='Show the implemented AstraCore feature toolkit count.')
 async def feature_count(self,i):await i.response.send_message(f'🧩 AstraCore currently exposes **{FEATURE_COUNT}+ callable production feature operations** across major systems.',ephemeral=True)
 @app_commands.command(name='runtime',description='Show runtime and shard capacity information.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def runtime(self,i):
  await i.response.send_message(f'⚙️ Guilds: `{len(self.bot.guilds)}` • Shards: `{self.bot.shard_count or 1}` • DB: `{await db.health()}` • Metrics events: `{sum(metrics.snapshot()["events"].values())}`',ephemeral=True)
async def setup(bot):await bot.add_cog(Platform(bot))
