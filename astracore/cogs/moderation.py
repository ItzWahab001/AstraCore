import discord,datetime
from discord import app_commands
from discord.ext import commands
from database.db import db
from services.mod_service import case,history
from utils.core import ok,err
class Moderation(commands.Cog):
 def __init__(self,bot):self.bot=bot
 async def logcase(self,i,m,kind,reason):
  cid=await case(i.guild.id,m.id,i.user.id,kind,reason); return cid
 @app_commands.command(name='warn',description='Create a moderation warning case.')
 @app_commands.checks.has_permissions(moderate_members=True)
 async def warn(self,i,m:discord.Member,reason:str='No reason provided'):cid=await self.logcase(i,m,'warn',reason);await i.response.send_message(embed=ok(f'Warning #{cid}',f'{m.mention}\n{reason}'))
 @app_commands.command(name='kick',description='Kick a member.')
 @app_commands.checks.has_permissions(kick_members=True)
 async def kick(self,i,m:discord.Member,reason:str='No reason provided'):
  if m==i.guild.owner or m.top_role>=i.guild.me.top_role:return await i.response.send_message(embed=err('Hierarchy','I cannot manage that member.'),ephemeral=True)
  await m.kick(reason=reason);cid=await self.logcase(i,m,'kick',reason);await i.response.send_message(embed=ok(f'Kick #{cid}',str(m)))
 @app_commands.command(name='ban',description='Ban a member.')
 @app_commands.checks.has_permissions(ban_members=True)
 async def ban(self,i,m:discord.Member,reason:str='No reason provided'):
  if m==i.guild.owner or m.top_role>=i.guild.me.top_role:return await i.response.send_message(embed=err('Hierarchy','I cannot manage that member.'),ephemeral=True)
  await m.ban(reason=reason);cid=await self.logcase(i,m,'ban',reason);await i.response.send_message(embed=ok(f'Ban #{cid}',str(m)))
 @app_commands.command(name='unban',description='Unban by user ID.')
 @app_commands.checks.has_permissions(ban_members=True)
 async def unban(self,i,user_id:str):
  try:u=await self.bot.fetch_user(int(user_id));await i.guild.unban(u,reason=f'Unban by {i.user}');cid=await self.logcase(i,u,'unban','Manual unban');await i.response.send_message(embed=ok(f'Unban #{cid}',str(u)))
  except (ValueError,discord.NotFound):await i.response.send_message(embed=err('Not found','Invalid or non-banned user ID.'),ephemeral=True)
 @app_commands.command(name='timeout',description='Timeout a member.')
 @app_commands.checks.has_permissions(moderate_members=True)
 async def timeout(self,i,m:discord.Member,minutes:app_commands.Range[int,1,40320],reason:str='No reason provided'):
  if m.top_role>=i.guild.me.top_role:return await i.response.send_message(embed=err('Hierarchy','I cannot timeout that member.'),ephemeral=True)
  await m.timeout(datetime.timedelta(minutes=minutes),reason=reason);cid=await self.logcase(i,m,'timeout',reason);await i.response.send_message(embed=ok(f'Timeout #{cid}',f'{m.mention} for {minutes} minutes'))
 @app_commands.command(name='untimeout',description='Remove a timeout.')
 @app_commands.checks.has_permissions(moderate_members=True)
 async def untimeout(self,i,m:discord.Member):await m.timeout(None,reason=f'Removed by {i.user}');await i.response.send_message(embed=ok('Timeout removed',str(m)))
 @app_commands.command(name='clear',description='Delete recent messages.')
 @app_commands.checks.has_permissions(manage_messages=True)
 async def clear(self,i,amount:app_commands.Range[int,1,100]):await i.response.defer(ephemeral=True);deleted=await i.channel.purge(limit=amount);await i.followup.send(f'🧹 Deleted {len(deleted)} messages.',ephemeral=True)
 @app_commands.command(name='cases',description='View moderation history.')
 @app_commands.checks.has_permissions(moderate_members=True)
 async def cases(self,i,user:discord.Member|None=None):
  rows=await history(i.guild.id,user.id if user else None);desc='\n'.join(f"`#{r['id']}` **{r['type']}** <@{r['user_id']}> — {r['reason'] or 'No reason'}" for r in rows) or 'No cases.';await i.response.send_message(embed=discord.Embed(title='📋 Moderation Cases',description=desc[:4000]))
 @app_commands.command(name='slowmode',description='Set channel slowmode in seconds.')
 @app_commands.checks.has_permissions(manage_channels=True)
 async def slowmode(self,i,seconds:app_commands.Range[int,0,21600]):await i.channel.edit(slowmode_delay=seconds,reason=f'Changed by {i.user}');await i.response.send_message(embed=ok('Slowmode updated',f'{seconds}s'))
 @app_commands.command(name='lock',description='Lock the current channel for @everyone.')
 @app_commands.checks.has_permissions(manage_channels=True)
 async def lock(self,i):await i.channel.set_permissions(i.guild.default_role,send_messages=False,reason=f'Locked by {i.user}');await i.response.send_message(embed=ok('Channel locked'))
 @app_commands.command(name='unlock',description='Unlock the current channel for @everyone.')
 @app_commands.checks.has_permissions(manage_channels=True)
 async def unlock(self,i):await i.channel.set_permissions(i.guild.default_role,send_messages=None,reason=f'Unlocked by {i.user}');await i.response.send_message(embed=ok('Channel unlocked'))
async def setup(bot):await bot.add_cog(Moderation(bot))
