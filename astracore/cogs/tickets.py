import discord
from discord import app_commands
from discord.ext import commands
from config import settings
from database.db import db
class TicketView(discord.ui.View):
 def __init__(self):super().__init__(timeout=None)
 @discord.ui.select(custom_id='astracore:ticket:v2',placeholder='Choose a ticket type…',options=[discord.SelectOption(label='Support',value='support',emoji='🛠️'),discord.SelectOption(label='Report',value='report',emoji='🚨'),discord.SelectOption(label='Partnership',value='partnership',emoji='🤝')])
 async def create(self,i,s):
  g=i.guild;over={g.default_role:discord.PermissionOverwrite(view_channel=False),i.user:discord.PermissionOverwrite(view_channel=True,send_messages=True,read_message_history=True)}
  if settings.staff_role_id and (r:=g.get_role(settings.staff_role_id)):over[r]=discord.PermissionOverwrite(view_channel=True,send_messages=True,read_message_history=True)
  cat=g.get_channel(settings.ticket_category_id) if settings.ticket_category_id else None;c=await g.create_text_channel(f'ticket-{i.user.name}'[:95],category=cat if isinstance(cat,discord.CategoryChannel) else None,overwrites=over);await db.execute('INSERT INTO tickets(guild_id,channel_id,opener_id) VALUES(?,?,?)',(g.id,c.id,i.user.id));await c.send(f'🎫 {i.user.mention} — **{s.values[0]}** ticket.',view=TicketControls());await i.response.send_message(f'Created {c.mention}.',ephemeral=True)
class TicketControls(discord.ui.View):
 def __init__(self):super().__init__(timeout=None)
 @discord.ui.button(label='Claim',style=discord.ButtonStyle.primary,emoji='🙋',custom_id='astracore:ticket:claim:v2')
 async def claim(self,i,b):
  if settings.staff_role_id and not (i.user.guild_permissions.administrator or any(r.id==settings.staff_role_id for r in i.user.roles)):return await i.response.send_message('Staff only.',ephemeral=True)
  await db.execute('UPDATE tickets SET claimed_by=? WHERE channel_id=?',(i.user.id,i.channel.id));await i.response.send_message(f'🙋 Claimed by {i.user.mention}.')
 @discord.ui.button(label='Close',style=discord.ButtonStyle.danger,emoji='🔒',custom_id='astracore:ticket:close:v2')
 async def close(self,i,b):await db.execute("UPDATE tickets SET status='closed',closed_at=CURRENT_TIMESTAMP WHERE channel_id=?",(i.channel.id,));await i.response.send_message('🔒 Closing ticket.');await i.channel.delete(reason=f'Closed by {i.user}')
class Tickets(commands.Cog):
 def __init__(self,bot):self.bot=bot
 @app_commands.command(name='ticket-panel',description='Post the ticket creation panel.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def panel(self,i):await i.response.send_message(embed=discord.Embed(title='🎫 AstraCore Support',description='Choose a category to create a private ticket.',color=discord.Color.blurple()),view=TicketView())
async def setup(bot):bot.add_view(TicketView());bot.add_view(TicketControls());await bot.add_cog(Tickets(bot))
