import random,discord
from discord import app_commands
from discord.ext import commands
class Fun(commands.Cog):
 def __init__(self,bot):self.bot=bot
 @app_commands.command(name='8ball',description='Ask the magic 8-ball.')
 async def ball(self,i,question:str):await i.response.send_message(f'🎱 {random.choice(["Yes.","No.","Maybe.","Probably.","Ask again later."])}')
 @app_commands.command(name='roll',description='Roll a die.')
 async def roll(self,i,sides:app_commands.Range[int,2,1000]=6):await i.response.send_message(f'🎲 **{random.randint(1,sides)}** / {sides}')
 @app_commands.command(name='coinflip',description='Flip a coin.')
 async def coin(self,i):await i.response.send_message(f'🪙 **{random.choice(["Heads","Tails"])}**')
 @app_commands.command(name='choose',description='Choose between comma-separated options.')
 async def choose(self,i,options:str):
  vals=[x.strip() for x in options.split(',') if x.strip()]
  if len(vals)<2:return await i.response.send_message('Provide at least two comma-separated options.',ephemeral=True)
  await i.response.send_message(f'🎯 I choose **{random.choice(vals)}**')
async def setup(bot):await bot.add_cog(Fun(bot))
