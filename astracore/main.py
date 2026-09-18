from __future__ import annotations
import logging,discord,time
from discord.ext import commands
from config import settings
from database.db import db
from database.migrations import apply_migrations
from observability.logging import configure
from observability.metrics import metrics
log=configure(settings.log_level)
EXTENSIONS=['cogs.core','cogs.configuration','cogs.moderation','cogs.automod','cogs.security','cogs.verification','cogs.welcome','cogs.tickets','cogs.music','cogs.ai','cogs.fun','cogs.leveling','cogs.economy','cogs.giveaways','cogs.community','cogs.tempvoice','cogs.roles','cogs.custom_commands','cogs.utilities','cogs.server','cogs.health','cogs.reminders','cogs.dashboard','cogs.platform']
class AstraCore(commands.Bot):
 def __init__(self):
  intents=discord.Intents.default();intents.members=True;intents.message_content=True;intents.guild_messages=True;intents.guild_reactions=True;intents.voice_states=True
  super().__init__(command_prefix=commands.when_mentioned,intents=intents,help_command=None)
 async def setup_hook(self):
  await db.init()
  await apply_migrations()
  metrics.inc('startup')
  for ext in EXTENSIONS:
   try:await self.load_extension(ext);log.info('Loaded %s',ext)
   except Exception:log.exception('Failed to load %s',ext)
  if settings.sync_commands:await self.tree.sync()
  metrics.inc('commands_synced')
 async def close(self):
  await db.close()
  await super().close()

 async def on_ready(self):
  await self.change_presence(status=discord.Status.dnd,activity=discord.Game(name=settings.status_text))
  log.info('Ready as %s | guilds=%d',self.user,len(self.guilds))
  metrics.inc('ready')
 async def on_app_command_error(self,i,error):
  original=getattr(error,'original',error);metrics.errors[type(original).__name__]+=1;log.exception('Command error',exc_info=original)
  if isinstance(original,discord.app_commands.errors.MissingPermissions):msg='❌ You do not have the required permissions.'
  elif isinstance(original,discord.Forbidden):msg='❌ Discord denied that action. Check permissions and role hierarchy.'
  elif isinstance(original,discord.HTTPException) and original.status==429:msg='⏳ Discord rate limit reached. Please try again.'
  else:msg='❌ Something went wrong. The incident was logged for administrators.'
  try:
   if i.response.is_done():await i.followup.send(msg,ephemeral=True)
   else:await i.response.send_message(msg,ephemeral=True)
  except discord.HTTPException: return
bot=AstraCore()
if __name__=='__main__':
 if not settings.token:raise SystemExit('DISCORD_TOKEN/BOT_TOKEN is missing. Configure .env.')
 bot.run(settings.token,log_handler=None)
