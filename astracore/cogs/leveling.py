import random,discord
from discord import app_commands
from discord.ext import commands
from database.db import db
class Leveling(commands.Cog):
 def __init__(self,bot):self.bot=bot;self.cool=set()
 @commands.Cog.listener()
 async def on_message(self,m):
  if m.author.bot or not m.guild:return
  k=(m.guild.id,m.author.id)
  if k in self.cool:return
  self.cool.add(k);xp=random.randint(8,15);row=await db.fetchone('SELECT xp,level FROM xp WHERE guild_id=? AND user_id=?',k);cur=row['xp'] if row else 0;lev=row['level'] if row else 0;cur+=xp
  new=cur//100
  await db.execute('INSERT INTO xp(guild_id,user_id,xp,level) VALUES(?,?,?,?) ON CONFLICT(guild_id,user_id) DO UPDATE SET xp=excluded.xp,level=excluded.level',(m.guild.id,m.author.id,cur,new))
  if new>lev: 
   try: await m.channel.send(f'🎉 {m.author.mention} reached **level {new}**!')
   except discord.HTTPException: return
  self.bot.loop.call_later(60,self.cool.discard,k)
 @app_commands.command(name='rank',description='Show your XP and level.')
 async def rank(self,i,user:discord.Member|None=None):
  u=user or i.user;r=await db.fetchone('SELECT xp,level FROM xp WHERE guild_id=? AND user_id=?',(i.guild.id,u.id));xp=r['xp'] if r else 0;lev=r['level'] if r else 0;await i.response.send_message(f'📈 **{u.display_name}** — Level **{lev}**, XP **{xp}**')
 @app_commands.command(name='leaderboard',description='Show the server XP leaderboard.')
 async def leaderboard(self,i):
  rows=await db.fetchall('SELECT user_id,xp,level FROM xp WHERE guild_id=? ORDER BY xp DESC LIMIT 10',(i.guild.id,));desc='\n'.join(f'**{n}.** <@{r["user_id"]}> — L{r["level"]} ({r["xp"]} XP)' for n,r in enumerate(rows,1)) or 'No XP data yet.';await i.response.send_message(embed=discord.Embed(title='📈 XP Leaderboard',description=desc))
 @app_commands.command(name='xp-set',description='Set a member XP amount.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def setxp(self,i,user:discord.Member,xp:app_commands.Range[int,0,100000000]):await db.execute('INSERT INTO xp(guild_id,user_id,xp,level) VALUES(?,?,?,?) ON CONFLICT(guild_id,user_id) DO UPDATE SET xp=excluded.xp,level=excluded.level',(i.guild.id,user.id,xp,xp//100));await i.response.send_message('✅ XP updated.',ephemeral=True)
 @app_commands.command(name='xp-add',description='Add XP to a member.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def addxp(self,i,user:discord.Member,xp:app_commands.Range[int,1,1000000]):r=await db.fetchone('SELECT xp FROM xp WHERE guild_id=? AND user_id=?',(i.guild.id,user.id));cur=(r['xp'] if r else 0)+xp;await db.execute('INSERT INTO xp(guild_id,user_id,xp,level) VALUES(?,?,?,?) ON CONFLICT(guild_id,user_id) DO UPDATE SET xp=excluded.xp,level=excluded.level',(i.guild.id,user.id,cur,cur//100));await i.response.send_message('✅ XP added.',ephemeral=True)
async def setup(bot):await bot.add_cog(Leveling(bot))
