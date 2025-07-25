
from SpeechSanitizer import SpeechSanitizer
from TTSAccents import TTSAccents
from VoiceStateChangeType import VoiceStateChangeType
from collections import deque
from dotenv import load_dotenv
from multiprocessing.dummy import active_children
from nextcord import Guild, VoiceChannel, VoiceClient
from nextcord import VoiceState, Member
from nextcord.ext import commands, tasks
from operator import truediv
import gtts
import json
import nextcord
import os
import re

# TODO have different class handle speech synthesis


class FILE_NAMES:
    ACCENT = "accent.txt"
    AUTOSPEAK = "autospeak.txt"


def save_accent(accent):
    with open(FILE_NAMES.ACCENT, "w+") as f:
        f.write(accent)


def save_autochatters(autochatters):
    with open(FILE_NAMES.AUTOSPEAK, "w+") as f:
        f.writelines([str(i) for i in autochatters])


class TTSBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.id = 542480024779882496
        self.path = os.getenv("MP3_PATH")
        # TODO make these into SpeechQueue class
        self.queue = deque()
        self.priority_queue = deque()
        self.auto_chatters = []
        # TODO move more accent functionallity to this (list, etc)
        self.accent_manager = TTSAccents()                  
        self.last_speaker = None
        self.speech_sanitizer = SpeechSanitizer(self.bot)
        

    @commands.Cog.listener()
    async def on_ready(self):
        self.speech_task.start()
        print("Speech task started")
        if os.path.exists(FILE_NAMES.ACCENT):
            with open(FILE_NAMES.ACCENT, "r") as f:
                self.accent_manager.current_accent = f.read().strip()
        if os.path.exists(FILE_NAMES.AUTOSPEAK):
            with open(FILE_NAMES.AUTOSPEAK, "r") as f:
                self.auto_chatters = [int(i) for i in f.readlines()]

    def _get_voice_state_change_type(self, before: VoiceState, after: VoiceState):
        state_type = None
        if before.channel and after.channel:
            if not before.self_mute and after.self_mute:
                state_type = VoiceStateChangeType.MUTE
            elif before.self_mute and not after.self_mute:
                state_type = VoiceStateChangeType.UNMUTE
            elif not before.self_deaf and after.self_deaf:
                state_type = VoiceStateChangeType.DEAFEN
            elif before.self_deaf and not after.self_deaf:
                state_type = VoiceStateChangeType.UNDEAFEN
            if not before.channel == after.channel:
                state_type = VoiceStateChangeType.SWAP
        elif after.channel and not before.channel:
            if after.self_mute:
                state_type = VoiceStateChangeType.JOIN_MUTED
            elif after.self_deaf:
                state_type = VoiceStateChangeType.JOIN_DEAFENED
            else:
                state_type = VoiceStateChangeType.JOIN
        elif before.channel and not after.channel:
            if before.self_mute:
                state_type = VoiceStateChangeType.LEAVE_MUTED
            elif before.self_deaf:
                state_type = VoiceStateChangeType.LEAVE_DEAFENED
            else:
                state_type = VoiceStateChangeType.LEAVE
    
        return state_type

    def _member_join(self, member: Member, voice_client: VoiceClient):
        if not member.id == self.id:
            text = f"{member.display_name} has joined the chat."
            self.priority_queue.append({"text": text, "vc": voice_client})

    async def _member_leave(self, member: Member, bot: commands.Bot, voice_client: VoiceClient, voice_state: VoiceState):
        if not member.id == self.id:
            text = f"{member.display_name} has left the chat."
            self.priority_queue.append({"text": text, "vc": voice_client})

        if len(voice_state.channel.members) == 1:
            if voice_state.channel.members[0].id == self.id:
                await voice_client.disconnect()
    
    def _get_channel_from_state_change(self, before: VoiceState, after: VoiceState, voice_state_change: VoiceStateChangeType):
        channel = None
        match voice_state_change:
            case VoiceStateChangeType.JOIN | \
                 VoiceStateChangeType.JOIN_MUTED | \
                 VoiceStateChangeType.JOIN_DEAFENED:
                channel = after.channel
            case _:
                channel = before.channel
                
        return channel
            
                
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        voice_state_change = self._get_voice_state_change_type(before, after)
        channel = None
        if not voice_state_change:
            return
            
        channel = self._get_channel_from_state_change(before, after, voice_state_change)
        
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

        match voice_state_change:
            case VoiceStateChangeType.JOIN | \
                    VoiceStateChangeType.JOIN_MUTED | \
                    VoiceStateChangeType.JOIN_DEAFENED:
                self._member_join(member, voice_client)
            case VoiceStateChangeType.LEAVE | \
                    VoiceStateChangeType.LEAVE_MUTED | \
                    VoiceStateChangeType.LEAVE_DEAFENED:
                await self._member_leave(member, bot, voice_client, before)
                

    @commands.command()
    async def join(self, ctx, *, channel: nextcord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def say(self, ctx: commands.Context, *, message):
        """Plays a file from the local filesystem"""
        
        text = self._smart_name_announce(message, ctx.author)
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
            return await ctx.send("Not connected to a voice channel. ")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command(aliases=["leave", "fuck off"])
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
                active_channels = []
                for channel in ctx.guild.voice_channels:
                    if len(channel.members) > 0:
                        active_channels.append(channel)
                print(active_channels)
                if len(active_channels) == 1:
                    c = active_channels[0]
                    await c.connect()
                    return True
                # await ctx.send("You are not connected to a voice channel. You can use \"moo join <channel>\" to connect.")
                return False
        return True
    
    @commands.command(pass_context=True)
    async def accent(self, ctx: commands.Context, arg: str):
        if arg == "list":
            await ctx.reply("Australia: AU\nUnited Kingdom: UK\n" +
                            "United States: US\nCanada: CA\n" +
                            "India: IN\nIreland: IE\nSouth Africa: SA")
            return
        if arg.upper() in self.accent_manager.accents :
            self.accent_manager.current_accent = self.accent_manager.accents[arg.upper()]
            await ctx.reply("Accent updated.")
            save_accent(self.accent_manager.current_accent)
            return
        await ctx.reply("Not a valid accent code.")
    
    @commands.group(pass_context=True)
    async def autospeak(self, ctx):
        pass
    
    @autospeak.command(pass_context=True)
    async def on(self, ctx: commands.Context):
        if ctx.author.id in self.auto_chatters:
            await ctx.reply("You already have auto chat enabled!")
            return
        
        self.auto_chatters.append(ctx.author.id)
        save_autochatters(self.auto_chatters)
        await ctx.reply("Auto chat has been enabled for you.")

    @autospeak.command(pass_context=True)
    async def off(self, ctx: commands.Context):
        if ctx.author.id not in self.auto_chatters:
            await ctx.reply("You already have auto chat disabled!")
            return
        self.auto_chatters.remove(ctx.author.id)
        save_autochatters(self.auto_chatters)
        await ctx.reply("Auto chat has been disabled for you.")

    def _smart_name_announce(self, message: str, author):
        if not author == self.last_speaker:
            self.last_speaker = author
            return f"{author.display_name} says {message}"
        
        return message 
    
    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        # hard code bad
        if message.channel.id in [931798323021631548, 852807298912485376, 966845116641857638]:
            if not message.content.lower().startswith("moo "):
                if message.author.id in self.auto_chatters:
                    ctx = await self.bot.get_context(message)
                    if await self.ensure_voice(ctx):
                        text = self._smart_name_announce(
                            message.content, message.author)
                    self.queue.append({"text": text, "context": ctx})

        # await self.bot.process_commands(message)
                  

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
                text = await self.speech_sanitizer.sanitize(item["text"], item["context"])
                voice_client = item["context"].voice_client
        if text and voice_client:
            print(text)
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
        if not voice_client.is_connected():
            return
        tts = gtts.gTTS(text, lang="en", tld=self.accent_manager.current_accent)
        tts.save(self.path)
        thing = nextcord.PCMVolumeTransformer(nextcord.FFmpegPCMAudio(self.path, options="-vn"))
        voice_client.play(thing)
        
        
if __name__ == "__main__":
    load_dotenv()
    bot = commands.Bot(command_prefix=("Moo ", "moo "))

    bot.add_cog(TTSBot(bot))
    bot.run(os.getenv('BOT_TOKEN'))
