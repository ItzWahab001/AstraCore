import discord
from utils.core import info
class HelpSelect(discord.ui.Select):
    def __init__(self):
        cats={'🛡️ Moderation':'warn, kick, ban, timeout, untimeout, cases, clear, slowmode, lock, unlock','🎵 Music':'play, pause, resume, skip, stop, queue, remove, shuffle, loop, volume, seek','🎫 Tickets':'ticket-panel, claim, close, reopen, add, remove','🔐 Security':'security, lockdown, unlockdown','📈 Leveling':'rank, leaderboard, xp-set, xp-add','💰 Economy':'balance, daily, work, pay, shop, inventory','🎉 Giveaways':'giveaway-create, giveaway-end, giveaway-reroll','💡 Community':'suggest, starboard, reminder','🤖 AI':'ai, teacher, ai-reset','⚙️ Admin':'config, modules'}
        self.cats=cats; super().__init__(placeholder='Choose a feature category…',options=[discord.SelectOption(label=k,value=k) for k in cats])
    async def callback(self,i): await i.response.edit_message(embed=info(self.values[0],self.cats[self.values[0]]),view=self.view)
class HelpView(discord.ui.View):
    def __init__(self): super().__init__(timeout=300);self.add_item(HelpSelect())
class Confirm(discord.ui.View):
    def __init__(self): super().__init__(timeout=60);self.value=None
    @discord.ui.button(label='Confirm',style=discord.ButtonStyle.danger)
    async def yes(self,i,b): self.value=True; await i.response.edit_message(content='Confirmed.',view=None);self.stop()
    @discord.ui.button(label='Cancel',style=discord.ButtonStyle.secondary)
    async def no(self,i,b): self.value=False; await i.response.edit_message(content='Cancelled.',view=None);self.stop()
