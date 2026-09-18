import discord,datetime,math,re
from discord import app_commands
from discord.ext import commands
class Utilities(commands.Cog):
 def __init__(self,bot):self.bot=bot
 @app_commands.command(name='avatar',description='Show a member avatar.')
 async def avatar(self,i,user:discord.User|None=None):u=user or i.user;e=discord.Embed(title=f'{u.display_name} avatar');e.set_image(url=u.display_avatar.url);await i.response.send_message(embed=e)
 @app_commands.command(name='roleinfo',description='Show role information.')
 async def roleinfo(self,i,role:discord.Role):await i.response.send_message(f'🎭 **{role.name}**\nID: `{role.id}`\nMembers: `{len(role.members)}`\nPosition: `{role.position}`\nMentionable: `{role.mentionable}`')
 @app_commands.command(name='channelinfo',description='Show current channel information.')
 async def channelinfo(self,i):c=i.channel;await i.response.send_message(f'📺 **{c.name}**\nID: `{c.id}`\nType: `{c.type}`\nCreated: {discord.utils.format_dt(c.created_at,"F")}')
 @app_commands.command(name='snowflake',description='Inspect a Discord snowflake.')
 async def snowflake(self,i,id_value:str):
  try:n=int(id_value);ts=((n>>22)+1420070400000)/1000;dt=datetime.datetime.fromtimestamp(ts,datetime.timezone.utc);await i.response.send_message(f'❄️ Created: {discord.utils.format_dt(dt,"F")} ({discord.utils.format_dt(dt,"R")})')
  except ValueError:await i.response.send_message('Invalid snowflake.',ephemeral=True)
 @app_commands.command(name='calc',description='Evaluate a safe arithmetic expression.')
 async def calc(self,i,expression:str):
  if len(expression)>100 or not re.fullmatch(r'[0-9+\-*/().% ]+',expression):return await i.response.send_message('Only basic arithmetic characters are allowed.',ephemeral=True)
  try:r=eval(expression,{'__builtins__':{}},{})
  except Exception:return await i.response.send_message('Invalid arithmetic expression.',ephemeral=True)
  if not isinstance(r,(int,float)) or not math.isfinite(r):return await i.response.send_message('Result is not finite.',ephemeral=True)
  await i.response.send_message(f'🧮 `{expression}` = **{r}**')
 @app_commands.command(name='timestamp',description='Create a Discord timestamp from a Unix timestamp.')
 async def timestamp(self,i,unix:int,style:str='F'):
  if style not in {'t','T','d','D','f','F','R'}:style='F'
  try:dt=datetime.datetime.fromtimestamp(unix,datetime.timezone.utc)
  except (OverflowError,OSError,ValueError):return await i.response.send_message('Invalid Unix timestamp.',ephemeral=True)
  await i.response.send_message(f'`{discord.utils.format_dt(dt,style)}`')
async def setup(bot):await bot.add_cog(Utilities(bot))
