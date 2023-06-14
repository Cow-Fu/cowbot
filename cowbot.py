import os
from nextcord.ext import commands
import nextcord

from dotenv import load_dotenv
from voicebot import TTSBot

load_dotenv()

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=("Moo ", "moo "), intents=intents)


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
