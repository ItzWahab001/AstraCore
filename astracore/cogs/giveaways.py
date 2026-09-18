import asyncio,random,datetime,discord
from discord import app_commands
from discord.ext import commands
from database.db import db
class GiveawayView(discord.ui.View):
 def __init__(self):super().__init__(timeout=None)
 @discord.ui.button(label='Enter',style=discord.ButtonStyle.success,emoji='🎉',custom_id='astracore:giveaway:enter')
 async def enter(self,i,b):
  rows=await db.fetchall('SELECT id FROM giveaways WHERE message_id=? AND status="running"',(i.message.id,))
  if not rows:return await i.response.send_message('Giveaway no longer exists.',ephemeral=True)
  gid=rows[0]['id']; existing=await db.fetchone('SELECT 1 FROM giveaway_entries WHERE giveaway_id=? AND user_id=?',(gid,i.user.id))
  if existing:
   await db.execute('DELETE FROM giveaway_entries WHERE giveaway_id=? AND user_id=?',(gid,i.user.id));return await i.response.send_message('↩️ Your entry was removed.',ephemeral=True)
  await db.execute('INSERT INTO giveaway_entries(giveaway_id,user_id) VALUES(?,?)',(gid,i.user.id));await i.response.send_message('🎉 Entry recorded.',ephemeral=True)
class Giveaways(commands.Cog):
 def __init__(self,bot):self.bot=bot;self.bot.loop.create_task(self.worker())
 async def worker(self):
  await self.bot.wait_until_ready()
  while not self.bot.is_closed():
   rows=await db.fetchall("SELECT * FROM giveaways WHERE status='running' AND ends_at<=?",(datetime.datetime.now(datetime.timezone.utc).isoformat(),))
   for r in rows:await self.end_row(r)
   await asyncio.sleep(10)
 async def end_row(self,r):
  ch=self.bot.get_channel(r['channel_id']);
  if ch:
   rows=await db.fetchall('SELECT user_id FROM giveaway_entries WHERE giveaway_id=?',(r['id'],));users=[]
   for x in rows:
    u=self.bot.get_user(x['user_id']) or await self.bot.fetch_user(x['user_id'])
    if u and not u.bot: users.append(u)
   winners=random.sample(users,min(r['winners'],len(users))) if users else []
   text=', '.join(x.mention for x in winners) if winners else 'No eligible entries.';await ch.send(f'🎉 Giveaway ended! **{r["prize"]}** — {text}')
  await db.execute("UPDATE giveaways SET status='ended' WHERE id=?",(r['id'],))
 @app_commands.command(name='giveaway-create',description='Create a giveaway using an ending time in minutes.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def create(self,i,minutes:app_commands.Range[int,1,10080],winners:app_commands.Range[int,1,20],prize:str):
  end=datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(minutes=minutes);e=discord.Embed(title='🎉 Giveaway',description=f'Prize: **{prize}**\nWinners: **{winners}**\nEnds: {discord.utils.format_dt(end,"R")}');await i.response.send_message(embed=e);msg=await i.original_response();await msg.add_reaction('🎉');await db.execute('INSERT INTO giveaways(guild_id,channel_id,message_id,ends_at,prize,winners) VALUES(?,?,?,?,?,?)',(i.guild.id,i.channel.id,msg.id,end.isoformat(),prize,winners))
 @app_commands.command(name='giveaway-end',description='End a giveaway immediately.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def end(self,i,message_id:int):
  r=await db.fetchone("SELECT * FROM giveaways WHERE guild_id=? AND message_id=? AND status='running'",(i.guild.id,message_id))
  if not r:return await i.response.send_message('Running giveaway not found.',ephemeral=True)
  await self.end_row(r);await i.response.send_message('🎉 Giveaway ended.',ephemeral=True)
 @app_commands.command(name='giveaway-reroll',description='Reroll a completed giveaway from its saved entries.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def reroll(self,i,message_id:int):
  r=await db.fetchone('SELECT * FROM giveaways WHERE guild_id=? AND message_id=?',(i.guild.id,message_id))
  if not r:return await i.response.send_message('Giveaway not found.',ephemeral=True)
  rows=await db.fetchall('SELECT user_id FROM giveaway_entries WHERE giveaway_id=?',(r['id'],));users=[]
  for x in rows:
   u=self.bot.get_user(x['user_id']) or await self.bot.fetch_user(x['user_id'])
   if u and not u.bot:users.append(u)
  if not users:return await i.response.send_message('No saved entries.',ephemeral=True)
  winners=random.sample(users,min(r['winners'],len(users)));await i.response.send_message('🔄 Reroll: '+', '.join(u.mention for u in winners))
async def setup(bot):await bot.add_cog(Giveaways(bot))
