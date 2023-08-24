import nextcord
from nextcord.ext import commands


class TestCog(commands.Cog):
    @nextcord.slash_command(description="Ping command")
    async def ping(self, interaction: nextcord.Interaction):
        await interaction.send("pong", ephemeral=True)
