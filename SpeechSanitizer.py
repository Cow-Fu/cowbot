

from collections import UserList
import re
import nextcord

from nextcord.ext import commands



class SpeechSanitizer:
    
    async def _sanitize_user(self, text: str, ctx: commands.Context):
        user_list = []

        for match in self.regex_user.finditer(text):
            full_match = match.group(0)
            id = int(match.group(1))
            print(id)

            user = await ctx.guild.fetch_member(id)
            user_list.append((full_match, f"@{user.display_name}"))
            
        for full_match, name in user_list:
            text = text.replace(full_match, name)
        return text    
        
    async def _sanitize_channel(self, text: str, ctx: commands.Context):
        channel_list = []       

        for match in self.regex_channel.finditer(text):
            full_match = match.group(0)
            id = int(match.group(1))

            channel = await ctx.guild.fetch_channel(id)
            channel_list.append((full_match, f"#{channel.name}"))

        for full_match, name in channel_list:
            text = text.replace(full_match, name)
        return text

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
