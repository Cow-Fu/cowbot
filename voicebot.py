
from dataclasses import dataclass
from collections import deque
from dotenv import load_dotenv
import gtts
import nextcord
from nextcord import VoiceState, Member, VoiceClient
from nextcord.ext import commands, tasks
from VoiceStateChangeType import VoiceStateChangeType
import os
from TTSAccents import TTSAccents
from SpeechSanitizer import SpeechSanitizer
from typing import Union
import asyncio


# TODO rename
@dataclass(slots=True)
class QueueObj:
    text: str
    ctx: commands.Context


@dataclass(slots=True)
class PriorityQueueObj:
    text: str
    vc: nextcord.VoiceClient


class ServerQueue:
    def __init__(self):
        self._queue = deque()
        self._priority_queue = deque()
        self._last_speaker = None

    @property
    def queue(self) -> deque[QueueObj]:
        return self._queue

    @property
    def priority_queue(self) -> deque[PriorityQueueObj]:
        return self._priority_queue

    @property
    def last_speaker(self) -> Member:
        return self._last_speaker

    @last_speaker.setter
    def last_speaker(self, member: Member):
        self._last_speaker = member

    def get_next(self) -> Union[QueueObj, PriorityQueueObj]:
        if not self.is_queue_empty():
            return self.priority_queue[0] if self.priority_queue else self.queue[0]
        return None

    def pop_next(self) -> Union[QueueObj, PriorityQueueObj]:
        if not self.is_queue_empty():
            return self.priority_queue.popleft() if self.priority_queue else self.queue.popleft()
        return None

    def is_queue_empty(self) -> bool:
        return not self.queue and not self.priority_queue


class ServerQueueManager:
    def __init__(self):
        self._server_queues: dict[int, ServerQueue] = {}

    def _ensure_id_exists(self, id: int):
        if id not in self._server_queues.keys():
            self._server_queues[id] = ServerQueue()

    def add_to_queue(self, id: int, queue_obj: QueueObj):
        self._ensure_id_exists(id)
        self._server_queues[id].queue.append(queue_obj)

    def add_to_priority_queue(self, id: int, queue_obj: PriorityQueueObj):
        self._ensure_id_exists(id)
        self._server_queues[id].priority_queue.append(queue_obj)

    def get_queues(self):
        return self._server_queues


# TODO have different class handle speech synthesis
class TTSBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.id = 542480024779882496
        self.path = os.getenv("MP3_PATH")
        self.server_queues = ServerQueueManager()
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

    def _priority_queue_add(self, obj: PriorityQueueObj):
        id = obj.vc.guild.id
        self.server_queues.add_to_priority_queue(id, obj)

    def _queue_add(self, obj: QueueObj):
        id = obj.ctx.message.guild.id
        self.server_queues.add_to_queue(id, obj)

    def _member_join(self, member: Member, voice_client: VoiceClient):
        text = f"{member.display_name} has joined the chat."
        self.server_queues.add_to_priority_queue(voice_client.guild.id, PriorityQueueObj(text=text, vc=voice_client))

    async def _member_leave(self, member: Member, bot: commands.Bot, voice_client: VoiceClient, voice_state: VoiceState):
        if len(voice_state.channel.members) == 1:
            if voice_state.channel.members[0].id == self.id:
                await voice_client.disconnect()
                return
        text = f"{member.display_name} has left the chat."
        self.server_queues.add_to_priority_queue(voice_client.guild.id, PriorityQueueObj(text=text, vc=voice_client))

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
        except AttributeError:
            return
        if not bot:
            return
        # each of these are voiceclient instances
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
        self.server_queues.add_to_queue(ctx.guild.id, QueueObj(text=text, ctx=ctx))

    # TODO: needs to connect to channel just like say
    @commands.command()
    async def ssay(self, ctx: commands.Context, *, message):
        self.server_queues.add_to_queue(ctx.guild.id, QueueObj(text=message, ctx=ctx))

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
                await ctx.send("You are not connected to a voice channel. You can use \"moo join <channel>\" to connect.")
                return False
        return True

    @commands.command(pass_context=True)
    async def accent(self, ctx: commands.Context, arg: str):
        if arg == "list":
            await ctx.reply("Australia: AU\nUnited Kingdom: UK\n" +
                            "United States: US\nCanada: CA\n" +
                            "India: IN\nIreland: IE\nSouth Africa: SA")
            return
        if arg.upper() in self.accent_manager.accents:
            self.accent_manager.current_accent = self.accent_manager.accents[arg.upper()]
            await ctx.reply("Accent updated.")
            return
        await ctx.reply("Not a valid accent code.")

    @commands.group(pass_context=True)
    async def autospeak(self, ctx):
        pass

    @autospeak.command(pass_context=True)
    async def on(self, ctx: commands.Context):
        if ctx.author in self.auto_chatters:
            await ctx.reply("You already have auto chat enabled!")
            return

        self.auto_chatters.append(ctx.author)
        await ctx.reply("Auto chat has been enabled for you.")

    @autospeak.command(pass_context=True)
    async def off(self, ctx: commands.Context):
        if not ctx.author not in self.auto_chatters:
            await ctx.reply("You already have auto chat disabled!")
            return
        self.auto_chatters.remove(ctx.author)
        await ctx.reply("Auto chat has been disabled for you.")

    def _smart_name_announce(self, message: str, author):
        if not author == self.last_speaker:
            self.last_speaker = author
            return f"{author.display_name} says {message}"

        return message

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.channel.id in [931798323021631548, 852807298912485376]: # hard code bad
            if not message.content.lower().startswith("moo "):
                if message.author in self.auto_chatters:
                    ctx = await self.bot.get_context(message)
                    if await self.ensure_voice(ctx):
                        text = self._smart_name_announce(message.content, message.author)
                    self.server_queues.add_to_queue(ctx.guild.id, QueueObj(text=text, ctx=ctx))
        # await self.bot.process_commands(message)

    @tasks.loop(seconds=1)
    async def speech_task(self):
        text = None
        voice_client = None
        for id, server in self.server_queues.get_queues().items():
            if server.is_queue_empty():
                # print("this bitch EmPtY")
                continue
            item = server.get_next()
            print(item)
            if isinstance(item, PriorityQueueObj):
                if self.voice_checks(item.vc):
                    server.pop_next()
                    text = item.text
                    voice_client = item.vc
            elif isinstance(item, QueueObj):
                if self.voice_checks(item.ctx):
                    server.pop_next()
                    text = await self.speech_sanitizer.sanitize(item.text, item.ctx)
                    voice_client = item.ctx.voice_client
            if text and voice_client:
                print(text)
                # await asyncio.sleep(.2)  # hack because it needs time to connect for the first message
                await self._speak_text(voice_client, text)

    def voice_checks(self, ctx_or_vc: Union[commands.Context, VoiceClient]):
        if ctx_or_vc:
            if isinstance(ctx_or_vc, commands.Context):
                if not ctx_or_vc.voice_client:
                    return False
                if ctx_or_vc.voice_client.is_playing():
                    return False
                return True
            if isinstance(ctx_or_vc, VoiceClient):
                if not ctx_or_vc.is_connected():
                    return False
                if ctx_or_vc.is_playing():
                    return False
                return True

    async def _speak_text(self, voice_client: VoiceClient, text: str):
        if not voice_client.is_connected():
            # todo, initial join message is ending up here
            print("not connected")
            return
        path = f"/dev/shm/{voice_client.guild.id}.mp3"
        accent = self.accent_manager.current_accent
        tts = await asyncio.get_event_loop().run_in_executor(None, lambda: gtts.gTTS(text, lang="en", tld=accent))
        tts.save(path)
        thing = nextcord.PCMVolumeTransformer(nextcord.FFmpegPCMAudio(path, options="-vn"))
        voice_client.play(thing)


if __name__ == "__main__":
    load_dotenv()
    bot = commands.Bot(command_prefix=("Moo ", "moo "))

    bot.add_cog(TTSBot(bot))
    bot.run(os.getenv('BOT_TOKEN'))
