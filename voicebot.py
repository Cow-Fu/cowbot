
import asyncio
from functools import singledispatch
from io import BytesIO
from itertools import chain
from pickle import TRUE
from queue import Queue
from collections import deque
from discord import Guild, VoiceClient
from dotenv import load_dotenv
import gtts
import nextcord
from nextcord import VoiceState, Member
from nextcord.ext import commands, tasks
import os

load_dotenv()

class TTSBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.id = 542480024779882496
        self.queue = deque()
        self.priority_queue = deque()
        # self.ctx = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.speech_task.start()
        
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        channel = after.channel
        if not channel:
            channel = before.channel
        bot = nextcord.utils.find(lambda x: x.id == self.id, channel.members)
        if not bot:
            return
        #each of these are voiceclient instances
        voice_client = nextcord.utils.find(lambda vc: vc.guild.id == bot.guild.id, self.bot.voice_clients)

        if not voice_client:
            return
        text = None
        if not before.channel and after.channel:
            text = f"{member.display_name} has joined the chat"
            self.priority_queue.append({"text": text, "vc": voice_client})
        elif before.channel and not after.channel:
            text = f"{member.display_name} has left the chat"
            self.priority_queue.append({"text": text, "vc": voice_client})
        

    @commands.command()
    async def join(self, ctx, *, channel: nextcord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def say(self, ctx: commands.Context, *, message):
        """Plays a file from the local filesystem"""
        
        self.ctx = ctx
        self.queue.append({"text": message, "context": ctx})

        # self.queue.append(f"{ctx.author.display_name} says: {query}")

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

    @tasks.loop(seconds=2)
    async def speech_task(self):
        text = None
        voice_client = None
        if self.priority_queue:
            if self.voice_checks(self.priority_queue[0]["vc"]):
                item = self.priority_queue.popleft()
                text = item["text"]
                voice_client = item["vc"]
        elif self.queue:
            if self.voice_checks(self.queue[0]["context"]):
                item = self.queue.popleft()
                text = item["text"]
                voice_client = item["context"].voice_client
        if text and voice_client:
            self._speak_text(voice_client, text)
    
    def voice_checks(self, ctx: commands.Context):
        if ctx:
            if isinstance(ctx, commands.Context):
                if not ctx.voice_client:
                    return False
                if ctx.voice_client.is_playing():
                    return False
                return True
            if isinstance(ctx, VoiceClient):
                if ctx.is_playing():
                    return False
                return True
            
    def _speak_text(self, voice_client: VoiceClient, text: str):
        tts = gtts.gTTS(text, lang="en")
        tts.save("/dev/shm/cowbot_audio.mp3")
        thing = nextcord.PCMVolumeTransformer(nextcord.FFmpegPCMAudio("/dev/shm/cowbot_audio.mp3", options="-vn"))
        voice_client.play(thing)
        
        
bot = commands.Bot(command_prefix=("Moo ", "moo "))

bot.add_cog(TTSBot(bot))
bot.run(os.getenv('BOT_TOKEN'))
