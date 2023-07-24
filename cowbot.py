import os
from nextcord.ext import commands, application_checks
import nextcord
from CogManager import CogManager

from dotenv import load_dotenv
from voicebot import TTSBot

load_dotenv()

GUILD_IDS = [852764173292142593]
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=("Moo ", "moo "), intents=intents, default_guild_ids=GUILD_IDS)

cog_manager = CogManager(bot)


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
@application_checks.has_guild_permissions(administrator=True)
async def cog(interaction: nextcord.Interaction):
    pass


@cog.subcommand()
@application_checks.has_guild_permissions(administrator=True)
async def load(interaction: nextcord.Interaction, cog_name: str):
    results = cog_manager.load_extention(cog_name)
    await interaction.send(results, ephemeral=True)


@cog.subcommand()
@application_checks.has_guild_permissions(administrator=True)
async def unload(interaction: nextcord.Interaction, cog_name: str):
    results = cog_manager.unload_extention(cog_name)
    await interaction.send(results, ephemeral=True)


@cog.subcommand()
@application_checks.has_guild_permissions(administrator=True)
async def reload(interaction: nextcord.Interaction, cog_name: str):
    results = cog_manager.reload_extention()
    await interaction.send(results, ephemeral=True)


@cog.subcommand()
@application_checks.has_guild_permissions(administrator=True)
async def list(interaction: nextcord.Interaction):
    await interaction.send("\n".join(cog_manager.get_active_extentions()))


@load.error
@unload.error
@reload.error
@list.error
async def user_no_permission_error(interaction: nextcord.Interaction, error):
    if isinstance(error, nextcord.errors.ApplicationCheckFailure):
        await interaction.send("No.", ephemeral=True)


print("\n".join(cog_manager.load_all_cogs()))

bot.add_cog(TTSBot(bot))
bot.run(os.getenv('BOT_TOKEN'))
