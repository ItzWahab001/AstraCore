import discord
from discord import app_commands
from discord.ext import commands
from config import settings
from views.verification import VerificationView
class Verification(commands.Cog):
 def __init__(self,bot):self.bot=bot
 @commands.Cog.listener()
 async def on_member_join(self,m):
  for rid in (settings.unverified_role_id,settings.default_role_id):
   if rid and (r:=m.guild.get_role(rid)):
    try:await m.add_roles(r,reason='AstraCore onboarding')
    except discord.HTTPException: return
 @app_commands.command(name='verification-panel',description='Post the verification panel.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def panel(self,i):await i.response.send_message(embed=discord.Embed(title='🔐 Verification',description='Click Verify to receive access.',color=discord.Color.green()),view=VerificationView())
async def setup(bot):bot.add_view(VerificationView());await bot.add_cog(Verification(bot))
