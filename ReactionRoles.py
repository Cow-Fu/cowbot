
import json
import os
import pathlib
from typing import Tuple
from discord import Member, Role
import nextcord
from nextcord.ext import commands


class ReactionRoles(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.allowed_roles = [852806140614279168]
        self.data_path = os.path.join(pathlib.Path().resolve(), os.getenv("REACTION_ROLES_JSON"))

        if not os.path.exists(self.data_path):
            with open(self.data_path, "w+") as f:
                f.write(json.dumps({"RoleMessageIDs": []}))
        with open(self.data_path, "r") as f:
            self.data = json.load(f)


    def _create_file(self, path):
        with open(self.data_path, "w+") as f:
            f.close()
            

    def _read_json(self, path):
        with open(path, "r") as fp:
            return json.load(fp)
        

    def _write_json(self, path, data):
        with open(path, "w") as f:
            json.dump(data, f)


    def _has_permission(self, ctx: commands.Context):
        return ctx.author.guild_permissions.administrator
    

    @commands.command()
    async def setup(self, ctx: commands.Context):
        if not self._has_permission(ctx):
            await ctx.reply("You do not have the right permission.")
            return

        if not ctx.message.reference:
            await ctx.reply("You need to reply to the message you want to setup for roles")
            return
                
        message: nextcord.Message
        message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        self.data["RoleMessageIDs"].append(message.id)
        self._write_json(self.data_path, self.data)
        

    async def _get_message_from_payload(self, payload: nextcord.RawReactionActionEvent)\
        -> Tuple[nextcord.Message, nextcord.TextChannel]:
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        return (message, channel)
        
    
    def _parse_message(self, message: nextcord.Message, payload: nextcord.RawReactionActionEvent):
        msgList = list(filter(lambda x: " :: " in x, message.content.split("\n")))
        
        pairs = []
        for item in msgList:
            split_message = item.split(" :: ")
            if not len(split_message) == 2:
                raise IndexError("Splitting message resulted in too many parts")
            emo, role = split_message[0], split_message[1]
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(int(role[3:-1]))
            pairs.append((emo.strip(), role))
        
        return pairs
    

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: nextcord.RawReactionActionEvent):
        if not payload.message_id in self.data["RoleMessageIDs"]:
            return

        message, channel = await self._get_message_from_payload(payload)
        emoji_role_pairs = self._parse_message(message, payload)

        for emoji, role in emoji_role_pairs:
            if str(payload.emoji) == emoji:
                await payload.member.add_roles(role)
                return
        
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: nextcord.RawReactionActionEvent):
        if not payload.message_id in self.data["RoleMessageIDs"]:
            return
        message, channel = await self._get_message_from_payload(payload)
        emoji_role_pairs = self._parse_message(message, payload)
        print(emoji_role_pairs)

        for emoji, role in emoji_role_pairs:
            if str(payload.emoji) == emoji:
                # use this to get the person
                member = channel.guild.get_member(payload.user_id)
                await member.remove_roles(role)
                return
        # lines = list(filter(message.content.split("\n"), lambda line: " :: " in line))
