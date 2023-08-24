import re
from nextcord.ext import commands


class SpeechSanitizer:
    async def _sanitize_user_or_channel(self, text: str, ctx: commands.Context, is_user: bool):
        obj_list = []
        regex = None
        prefix = None
        func = None
        if is_user:
            regex = self.regex_user
            prefix = "@"
            func = ctx.guild.fetch_member
        else:
            regex = self.regex_channel
            prefix = "#"
            func = ctx.guild.fetch_channel

        for match in regex.finditer(text):
            full_match = match.group(0)
            id = int(match.group(1))

            obj = await func(id)
            obj_list.append((full_match, f"{prefix} {obj.display_name if is_user else obj.name}"))

        for full_match, name in obj_list:
            text = text.replace(full_match, name)
        return text

    async def _sanitize_user(self, text: str, ctx: commands.Context):
        return await self._sanitize_user_or_channel(text, ctx, True)

    async def _sanitize_channel(self, text: str, ctx: commands.Context):
        return await self._sanitize_user_or_channel(text, ctx, False)

    async def sanitize(self, text, ctx: commands.Context):
        text = self.regex_url.sub("link", text)
        text = self.regex_emoji.sub(lambda m: m.group(1), string=text)
        text = await self._sanitize_user(text, ctx)
        text = await self._sanitize_channel(text, ctx)
        return text

    def __init__(self, client: commands.Bot):
        self.regex_emoji = re.compile("<:(\w+):(\d+)>")
        self.regex_user = re.compile("<@(\d+)>")
        self.regex_channel = re.compile("<#(\d+)>")
        self.regex_url = re.compile("http\S+")
        self.client = client
