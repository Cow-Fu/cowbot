import os
from nextcord.ext import commands, application_checks
import nextcord
from nextcord.ext.commands import errors as nc_errors
from CogManager import CogManager

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


@bot.slash_command()
async def cog(interaction: nextcord.Interaction):
    pass


@cog.subcommand()
@commands.check_any(commands.is_owner())
async def load(interaction: nextcord.Interaction, cog_name: str):
    responce = None
    try:
        bot.load_extension(cog_name)
    except nc_errors.ExtensionNotFound:
        responce = f"Extention: '{cog_name}' not found."
    except nc_errors.ExtensionAlreadyLoaded:
        responce = f"Extention: '{cog_name}' already loaded."
    except nc_errors.NoEntryPointError:
        responce = f"Extention: '{cog_name}' does not have a setup function."
    except nc_errors.ExtensionFailed:
        responce = f"Extention: '{cog_name}' the extention or setup function had an execution error."
    finally:
        await interaction.send(responce if responce else f"Successfully loaded: '{cog_name}'", ephemeral=True)


@cog.subcommand()
@commands.check_any(commands.is_owner())
async def unload(interaction: nextcord.Interaction, cog_name: str):
    responce = None
    try:
        bot.unload_extension(cog_name)
    except nc_errors.ExtensionNotFound:
        responce = f"Extention: '{cog_name}' not found."
    except nc_errors.ExtensionNotLoaded:
        responce = f"Extention: '{cog_name}' is not currently loaded."
    finally:
        await interaction.send(responce if responce else f"Successfully unloaded: '{cog_name}'", ephemeral=True)


@cog.subcommand()
@commands.check_any(commands.is_owner())
async def reload(interaction: nextcord.Interaction, cog_name: str):
    responce = None
    try:
        bot.reload_extension(cog_name)
    except nc_errors.ExtensionNotLoaded:
        responce = f"Extention: '{cog_name}' is not currently loaded."
    except nc_errors.ExtensionNotFound:
        responce = f"Extention: '{cog_name}' not found."
    except nc_errors.NoEntryPointError:
        responce = f"Extention: '{cog_name}' does not have a setup function."
    except nc_errors.ExtensionFailed:
        responce = f"Extention: '{cog_name}' the extention or setup function had an execution error."
    finally:
        await interaction.send(responce if responce else f"Successfully unloaded: '{cog_name}'", ephemeral=True)


extentions = None
for root, dirs, files in os.walk("cogs"):
    extentions = [f"{root}.{dir}" for dir in dirs]
    break
for e in extentions:
    bot.load_extension(e)
    print(f"Loading: {e}")

bot.add_cog(TTSBot(bot))
bot.run(os.getenv('BOT_TOKEN'))
