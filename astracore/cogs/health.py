import time,discord
from discord import app_commands
from discord.ext import commands
from database.db import db
from observability.metrics import metrics
from services.health import build_health
class Health(commands.Cog):
 def __init__(self,bot):self.bot=bot;self.started=time.time()
 @app_commands.command(name='health',description='Show bot, database and media health.')
 async def health(self,i):
  status=await db.health();h=build_health(self.started,status)
  snap=metrics.snapshot();errors=sum(snap['errors'].values())
  e=discord.Embed(title='💚 AstraCore Health',description=f'Status: **{h.status}**\nLatency: **{round(self.bot.latency*1000)}ms**\nUptime: **{int(h.uptime)}s**\nGuilds: **{len(self.bot.guilds)}**\nDatabase: **{h.database}**\nFFmpeg: **{"ready" if h.ffmpeg else "missing"}**\nErrors recorded: **{errors}**')
  await i.response.send_message(embed=e,ephemeral=True)
 @app_commands.command(name='metrics',description='Show runtime metrics.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def metrics_cmd(self,i):
  s=metrics.snapshot();await i.response.send_message(f'```json\n{__import__("json").dumps(s,indent=2)[:3800]}\n```',ephemeral=True)
 @app_commands.command(name='shardinfo',description='Show shard information.')
 async def shardinfo(self,i):await i.response.send_message(f'🛰️ Shard ID: `{i.guild.shard_id}`',ephemeral=True)
async def setup(bot):await bot.add_cog(Health(bot))
