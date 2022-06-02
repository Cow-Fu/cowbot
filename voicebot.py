
from collections import deque
from discord import Guild, VoiceChannel, VoiceClient
from dotenv import load_dotenv
import gtts
import nextcord
from nextcord import VoiceState, Member
from nextcord.ext import commands, tasks
from VoiceStateChangeType import VoiceStateChangeType
import os


class TTSBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.id = 542480024779882496
        self.path = os.getenv("MP3_PATH")
        self.queue = deque()
        self.priority_queue = deque()
    
        self.accents = {
            "US": "com",
            "AU": "com.au",
            "UK": "co.uk",
            "CA": "ca",
            "IN": "co.in",
            "IE": "ie",
            "SA": "co.za"
        }
        
        self.currentAccent = self.accents["US"]

    @commands.Cog.listener()
    async def on_ready(self):
        self.speech_task.start()
        print("Speech task started")

    def _get_voice_state_change_type(self, before: VoiceState, after: VoiceState):
        stateType = None
        if before.channel:
            if before.self_mute:
                return VoiceStateChangeType.MUTE
            if before.self_deaf:
                return VoiceStateChangeType.DEAFEN
            if after.channel:
                return VoiceStateChangeType.SWAP
            if not after.channel:
                return VoiceStateChangeType.LEAVE
        if after.channel:
            # might not need these
            if after.self_mute:
                return VoiceStateChangeType.MUTE
            if after.self_deaf:
                return VoiceStateChangeType.DEAFEN
            return VoiceStateChangeType.JOIN
        else:
            return None
        
    def _member_join(self, member: Member, voice_client: VoiceClient):
        text = f"{member.display_name} has joined the chat."
        self.priority_queue.append({"text": text, "vc": voice_client})
        
    async def _member_leave(self, member: Member, bot: commands.Bot, voice_client: VoiceClient, voice_state: VoiceState):
        text = f"{member.display_name} has left the chat."
        self.priority_queue.append({"text": text, "vc": voice_client})
        
        if len(voice_state.channel.members) == 1:
            if voice_state.channel.members[0].id == self.id:
                await voice_client.disconnect()
                
                
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        voice_state_change = self._get_voice_state_change_type(before, after)
        channel = None
        if not voice_state_change:
            return
            
        if voice_state_change == VoiceStateChangeType.JOIN:
            channel = after.channel
        else:
            channel = before.channel
        
        try:
            bot = nextcord.utils.find(lambda x: x.id == self.id, channel.members)
        except AttributeError as e:
            return
        if not bot:
            return
        #each of these are voiceclient instances
        voice_client = nextcord.utils.find(lambda vc: vc.guild.id == bot.guild.id, self.bot.voice_clients)

        if not voice_client:
            return

        if voice_state_change == VoiceStateChangeType.JOIN:
            self._member_join(member, voice_client)
        elif voice_state_change == VoiceStateChangeType.LEAVE:
            await self._member_leave(member, bot, voice_client, before)
        else:
            return

    @commands.command()
    async def join(self, ctx, *, channel: nextcord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def say(self, ctx: commands.Context, *, message):
        """Plays a file from the local filesystem"""
        
        text = f"{ctx.author.display_name} says {message}"
        self.queue.append({"text": text, "context": ctx})

        # self.queue.append(f"{ctx.author.display_name} says: {query}")

    # TODO: needs to connect to channel just like say
    @commands.command()
    async def ssay(self, ctx: commands.Context, *, message):
        self.queue.append({"text": message, "context": ctx})

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
    @ssay.before_invoke
    async def ensure_voice(self, ctx: commands.Context):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
    
    @commands.command(pass_context=True)
    async def accent(self, ctx: commands.Context, arg: str):
        if arg == "list":
            await ctx.reply("Australia: AU\nUnited Kingdom: UK\n" +
                            "United States: US\nCanada: CA\n" +
                            "India: IN\nIreland: IE\nSouth Africa: SA")
            return
        if arg.upper() in self.accents:
            self.currentAccent = self.accents[arg.upper()]
            await ctx.reply("Accent updated.")
            return
        await ctx.reply("Not a valid accent code.")
            

    @tasks.loop(seconds=1.5)
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
            
    # @tasks.loop(seconds=5)
    # async def auto_leave(self):
    #     for guild in self.bot.guilds:
    #         for voice_channel in guild.voice_channels:
    #             if len(voice_channel.members) == 1:
    #                 member = voice_channel.members[0]
    #                 if member.id == self.id:
    #                     return
    #                 bot = member
    #                 voice_client: VoiceClient
    #                 voice_client = nextcord.utils.find(lambda vc: vc.guild.id == bot.guild.id, self.bot.voice_clients)
    #                 if voice_client.is_connected():
    #                     await voice_client.disconnect()
    #                     self.queue.clear()
                        
    
    def _speak_text(self, voice_client: VoiceClient, text: str):
        if not voice_client.is_connected():
            return
        tts = gtts.gTTS(text, lang="en", tld=self.currentAccent)
        try:
            tts.save(self.path)
        except AssertionError as e:
            return
        thing = nextcord.PCMVolumeTransformer(nextcord.FFmpegPCMAudio(self.path, options="-vn"))
        voice_client.play(thing)
        
        
if __name__ == "__main__":
    load_dotenv()
    bot = commands.Bot(command_prefix=("Moo ", "moo "))

    bot.add_cog(TTSBot(bot))
    bot.run(os.getenv('BOT_TOKEN'))
