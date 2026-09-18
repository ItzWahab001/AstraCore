import discord
from services.config_service import get, set_value
from services.player import manager
from services.health import build_health

PANELS={
'🛡️ Moderation':'moderation_enabled','🤖 AutoMod':'automod_enabled','🔐 Security':'security_enabled','🎵 Music':'music_enabled','🎫 Tickets':'tickets_enabled','✅ Verification':'verification_enabled','👋 Welcome':'welcome_enabled','📈 Leveling':'leveling_enabled','💰 Economy':'economy_enabled','🎉 Giveaways':'giveaways_enabled','🎭 Roles':'roles_enabled','🔊 Temp Voice':'tempvoice_enabled','💡 Suggestions':'suggestions_enabled','⭐ Starboard':'starboard_enabled','🤖 AI':'ai_enabled','⚙️ Server Settings':'dashboard_enabled'}

class PanelSelect(discord.ui.Select):
    def __init__(self,view):
        self.parent_view=view
        super().__init__(placeholder='Select a system…',options=[discord.SelectOption(label=k,value=k) for k in PANELS])
    async def callback(self,i):self.parent_view.selected=self.values[0];await self.parent_view.render(i)

class PremiumDashboard(discord.ui.View):
    def __init__(self,bot,guild_id):super().__init__(timeout=900);self.bot=bot;self.guild_id=guild_id;self.selected='⚙️ Server Settings';self.add_item(PanelSelect(self))
    async def render(self,i):
        cfg=await get(self.guild_id);key=PANELS[self.selected];enabled=cfg.get(key,True)
        if self.selected=='🎵 Music':
            p=manager.get(self.guild_id);extra=f'\nNow Playing: **{p.current.title if p.current else "Idle"}**\nQueue: **{len(p.queue)}**'
        elif self.selected=='🔐 Security':extra=f'\nAuto-lockdown: **{cfg.get("auto_lockdown",False)}**\nRaid threshold: **{cfg.get("raid_join_threshold",20)}**'
        else:extra=''
        embed=discord.Embed(title=f'AstraCore • {self.selected}',description=f'**Enabled:** `{enabled}`\n**Config key:** `{key}`{extra}\n\nUse the buttons below to change this system safely.')
        await i.response.edit_message(embed=embed,view=self)
    @discord.ui.button(label='Enable',emoji='🟢',style=discord.ButtonStyle.success)
    async def enable(self,i,b):await set_value(self.guild_id,PANELS[self.selected],True);await self.render(i)
    @discord.ui.button(label='Disable',emoji='🔴',style=discord.ButtonStyle.danger)
    async def disable(self,i,b):await set_value(self.guild_id,PANELS[self.selected],False);await self.render(i)
    @discord.ui.button(label='Refresh',emoji='🔄',style=discord.ButtonStyle.secondary)
    async def refresh(self,i,b):await self.render(i)
    @discord.ui.button(label='Close',emoji='✖️',style=discord.ButtonStyle.secondary)
    async def close(self,i,b):await i.response.edit_message(content='Panel closed.',embed=None,view=None);self.stop()
