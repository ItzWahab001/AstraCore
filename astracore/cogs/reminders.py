import datetime,discord
from discord import app_commands
from discord.ext import commands
from database.db import db
class Reminders(commands.Cog):
 def __init__(self,bot):self.bot=bot;self.bot.loop.create_task(self.worker())
 async def worker(self):
  await self.bot.wait_until_ready()
  while not self.bot.is_closed():
   now=datetime.datetime.now(datetime.timezone.utc).isoformat();rows=await db.fetchall("SELECT * FROM reminders WHERE status='pending' AND due_at<=?",(now,))
   for r in rows:
    ch=self.bot.get_channel(r['channel_id']) if r['channel_id'] else None
    if ch:
     try:await ch.send(f'⏰ <@{r["user_id"]}> reminder: {r["content"]}')
     except discord.HTTPException: return
    if r['recurring_seconds']:
     due=datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=r['recurring_seconds']);await db.execute('UPDATE reminders SET due_at=? WHERE id=?',(due.isoformat(),r['id']))
    else:await db.execute("UPDATE reminders SET status='done' WHERE id=?",(r['id'],))
   await discord.utils.sleep_until(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=20))
 @app_commands.command(name='remind',description='Create a persistent reminder in minutes.')
 async def remind(self,i,minutes:app_commands.Range[int,1,525600],text:str):
  due=datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(minutes=minutes);rid=await db.execute('INSERT INTO reminders(guild_id,user_id,channel_id,content,due_at) VALUES(?,?,?,?,?)',(i.guild.id,i.user.id,i.channel.id,text,due.isoformat()));await i.response.send_message(f'⏰ Reminder #{rid} set for {discord.utils.format_dt(due,"R")}')
 @app_commands.command(name='reminders',description='List your active reminders.')
 async def reminders(self,i):rows=await db.fetchall("SELECT id,content,due_at FROM reminders WHERE user_id=? AND status='pending' ORDER BY due_at",(i.user.id,));d='\n'.join(f'`#{r["id"]}` {r["content"]} — {r["due_at"]}' for r in rows) or 'No active reminders.';await i.response.send_message(d,ephemeral=True)
 @app_commands.command(name='remind-delete',description='Delete one of your reminders.')
 async def delete(self,i,reminder_id:int):await db.execute("UPDATE reminders SET status='deleted' WHERE id=? AND user_id=?",(reminder_id,i.user.id));await i.response.send_message('🗑️ Reminder deleted.',ephemeral=True)
async def setup(bot):await bot.add_cog(Reminders(bot))
