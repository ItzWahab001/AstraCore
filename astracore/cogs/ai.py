import discord
from discord import app_commands
from discord.ext import commands
from services.ai_service import ask
from utils.core import rate
class AI(commands.Cog):
 def __init__(self,bot):self.bot=bot
 async def run(self,i,prompt,system):
  if not rate.allow((i.guild.id,i.user.id,'ai'),5,60):return await i.response.send_message('⏳ AI rate limit reached. Try again shortly.',ephemeral=True)
  await i.response.defer()
  try:a=await ask(prompt,system);await i.followup.send(a[:4000])
  except Exception as e:await i.followup.send('❌ AI request failed. Check the provider configuration and logs.')
 @app_commands.command(name='ai',description='Ask the configured AI provider.')
 async def ai(self,i,prompt:app_commands.Range[str,1,2000]):await self.run(i,prompt,'You are AstraCore, a helpful Discord assistant. Be concise and safe.')
 @app_commands.command(name='teacher',description='Get a structured educational explanation.')
 async def teacher(self,i,question:app_commands.Range[str,1,2000]):await self.run(i,question,'You are a patient tutor. Explain with headings, examples, and a short recap.')
async def setup(bot):await bot.add_cog(AI(bot))
