import discord
from config import settings
class VerificationView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label='Verify',emoji='✅',style=discord.ButtonStyle.success,custom_id='astracore:verify:v2')
    async def verify(self,i,b):
        if not i.guild:return
        vr=i.guild.get_role(settings.verified_role_id); ur=i.guild.get_role(settings.unverified_role_id)
        if not vr:return await i.response.send_message('Verification is not configured correctly.',ephemeral=True)
        try:
            if ur: await i.user.remove_roles(ur,reason='AstraCore verification')
            await i.user.add_roles(vr,reason='AstraCore verification')
            await i.response.send_message('✅ Verification complete.',ephemeral=True)
        except discord.Forbidden: await i.response.send_message('Bot lacks role-management permission or hierarchy.',ephemeral=True)
