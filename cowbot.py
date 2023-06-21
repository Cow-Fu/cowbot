import os
from nextcord.ext import commands
import nextcord

from dotenv import load_dotenv
from voicebot import TTSBot

load_dotenv()

GUILD_IDS = [852764173292142593]
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=("Moo ", "moo "), intents=intents, default_guild_ids=GUILD_IDS)


@bot.event
async def on_ready():
    print("connected")


@bot.group(pass_context=True)
async def guess(ctx):
    pass


@guess.command()
async def what(ctx: commands.Context):
    await ctx.channel.send("Chicken butt")

extentions = None
for root, dirs, files in os.walk("cogs"):
    extentions = [f"{root}.{dir}" for dir in dirs]
    break
for e in extentions:
    bot.load_extension(e)
    print(f"Loading: {e}")

bot.add_cog(TTSBot(bot))
bot.run(os.getenv('BOT_TOKEN'))
