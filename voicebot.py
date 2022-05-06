
from io import BytesIO
from queue import Queue
from collections import deque
from discord import AudioSource
from dotenv import load_dotenv
import gtts
import nextcord
from nextcord.ext import commands, tasks
import os

load_dotenv()

class TTSBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queue = deque()

    @commands.command()
    async def join(self, ctx, *, channel: nextcord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def say(self, ctx: commands.Context, *, query):
        """Plays a file from the local filesystem"""

        tts = gtts.gTTS(query, lang="en")
        tts.save("/dev/shm/cowbot_audio.mp3")
        thing = nextcord.PCMVolumeTransformer(nextcord.FFmpegPCMAudio("/dev/shm/cowbot_audio.mp3", options="-vn"))
        ctx.voice_client.play(thing, after=lambda e: print(f'Player error: {e}') if e else None)

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command(aliases=["leave", "fuckoff"])
    async def stop(self, ctx: commands.Context):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()
    
    @say.before_invoke
    async def ensure_voice(self, ctx: commands.Context):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop() 

bot = commands.Bot(command_prefix=("Moo ", "moo "))

bot.add_cog(TTSBot(bot))
bot.run(os.getenv('BOT_TOKEN'))
