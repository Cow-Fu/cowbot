
import json
import os
from discord import Role
import nextcord
from nextcord.ext import commands


class ReactionRoles(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.allowed_roles = [852806140614279168]
        self.data_path = os.getenv("REACTION_ROLES_JSON")

        if not os.path.exists(self.data_path):
            with open(self.data_path, "w+") as f:
                f.write(json.dumps({"RoleMessageIDs": []}))
        self.data = json.load(self.data_path)
    
    def _create_file(self, path):
        with open(self.data_path, "w+") as f:
            f.close()
            
    def _read_json(self, path):
        with open(path, "r") as f:
            return json.load(f)
        
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
        message = await ctx.channel.fetch_message(ctx.message.reference)
        self.data["RoleMessageIDs"].append(message.id)
        self._write_json(self.data_path, self.data)
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: nextcord.RawReactionActionEvent):
        if not payload.message_id in self.data["RoleMessageIDs"]:
            return
        return
        # lines = list(filter(message.content.split("\n"), lambda line: " :: " in line))
