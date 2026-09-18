import random,time,discord
from discord import app_commands
from discord.ext import commands
from database.db import db
async def bal(g,u):
 r=await db.fetchone('SELECT balance FROM economy WHERE guild_id=? AND user_id=?',(g,u));return r['balance'] if r else 0
async def change(g,u,a,kind):
 await db.execute('INSERT INTO economy(guild_id,user_id,balance) VALUES(?,?,?) ON CONFLICT(guild_id,user_id) DO UPDATE SET balance=balance+excluded.balance',(g,u,a));await db.execute('INSERT INTO transactions(guild_id,user_id,kind,amount) VALUES(?,?,?,?)',(g,u,kind,a))
class Economy(commands.Cog):
 def __init__(self,bot):self.bot=bot;self.daily={};self.work={}
 @app_commands.command(name='balance',description='Show an economy balance.')
 async def balance(self,i,user:discord.Member|None=None):u=user or i.user;await i.response.send_message(f'💰 {u.mention} has **{await bal(i.guild.id,u.id):,}** credits.')
 @app_commands.command(name='daily',description='Claim a daily reward.')
 async def daily(self,i):
  k=(i.guild.id,i.user.id);now=time.time()
  if now-self.daily.get(k,0)<86400:return await i.response.send_message('⏳ Your daily reward is still on cooldown.',ephemeral=True)
  self.daily[k]=now;a=random.randint(100,250);await change(*k,a,'daily');await i.response.send_message(f'🎁 You received **{a}** credits.')
 @app_commands.command(name='work',description='Work for credits.')
 async def work(self,i):
  k=(i.guild.id,i.user.id);now=time.time()
  if now-self.work.get(k,0)<300:return await i.response.send_message('⏳ Work is on cooldown.',ephemeral=True)
  self.work[k]=now;a=random.randint(40,120);await change(*k,a,'work');await i.response.send_message(f'💼 You earned **{a}** credits.')
 @app_commands.command(name='pay',description='Transfer credits to another member.')
 async def pay(self,i,user:discord.Member,amount:app_commands.Range[int,1,1000000]):
  if user.bot or user.id==i.user.id:return await i.response.send_message('Choose another human member.',ephemeral=True)
  if await bal(i.guild.id,i.user.id)<amount:return await i.response.send_message('Insufficient balance.',ephemeral=True)
  await change(i.guild.id,i.user.id,-amount,'transfer_out');await change(i.guild.id,user.id,amount,'transfer_in');await i.response.send_message(f'💸 Sent **{amount:,}** credits to {user.mention}.')
 @app_commands.command(name='economy-top',description='Show the economy leaderboard.')
 async def top(self,i):rows=await db.fetchall('SELECT user_id,balance FROM economy WHERE guild_id=? ORDER BY balance DESC LIMIT 10',(i.guild.id,));desc='\n'.join(f'**{n}.** <@{r["user_id"]}> — {r["balance"]:,}' for n,r in enumerate(rows,1)) or 'No balances yet.';await i.response.send_message(embed=discord.Embed(title='💰 Economy',description=desc))
async def setup(bot):await bot.add_cog(Economy(bot))
