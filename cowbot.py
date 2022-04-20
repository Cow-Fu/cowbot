from contextvars import Context
import os
from nextcord.ext import commands

from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix="moo ")

@bot.event
async def on_ready():
    print("connected")
    
@bot.group(pass_context=True)
async def guess(ctx):
    pass

@guess.command()
async def what(ctx: commands.Context):
    await ctx.channel.send("Chicken butt")

bot.run(os.getenv('BOT_TOKEN'))