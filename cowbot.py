from contextvars import Context
import os
from nextcord.ext import commands

from dotenv import load_dotenv
from voicebot import TTSBot

load_dotenv()

bot = commands.Bot(command_prefix=("Moo ", "moo "))

@bot.event
async def on_ready():
    print("connected")
    
@bot.group(pass_context=True)
async def guess(ctx):
    pass

@guess.command()
async def what(ctx: commands.Context):
    await ctx.channel.send("Chicken butt")

bot.add_cog(TTSBot(bot))
bot.run(os.getenv('BOT_TOKEN'))
