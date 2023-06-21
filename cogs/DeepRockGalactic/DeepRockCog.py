import nextcord
from nextcord.ext import commands
from requests import get
import json
from dataclasses import dataclass
from typing import List, Optional
import asyncio
from enum import Enum


@dataclass
class StageInfo:
    id: int
    primary: str
    secondary: str
    anomaly: Optional[str]
    warning: Optional[str]


@dataclass
class DeepDiveInfo:
    type: str
    name: str
    biome: str
    seed: int
    stages: List[StageInfo]

class DeepDiveType(Enum):
    DEEP_DIVE = "Deep Dive"
    ELITE_DEEP_DIVE = "Elite Deep Dive"


class DeepDiveManager:
    _URL = "https://drgapi.com/v1/deepdives"

    def __init__(self):
        self.deep_dive_info = None

    async def _fetch_info(self):
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: get(DeepDiveManager._URL).content)
        return json.loads(result)

    def _build(self, variant: dict):
        stages = []
        for stage in variant.pop("stages"):
            stages.append(StageInfo(**stage))
        variant["stages"] = stages
        return DeepDiveInfo(**variant)

    async def get_info(self) -> DeepDiveInfo:
        info = await self._fetch_info()
        normal_dd = self._build(info["variants"][0])
        elite_dd = self._build(info["variants"][1])
        return [normal_dd, elite_dd]


class DeepDiveEmbed:
    def __init__(self):
        self.deepdive = None
        self.stages = []

    def _buildMainEmbed(self, dd: DeepDiveInfo):
        embed = nextcord.Embed(title=dd.type)
        embed.add_field(name="Code Name", value=dd.name, inline=True)
        embed.add_field(name="Biome", value=dd.biome, inline=True)
        return embed

    def _buildStageEmbed(self, stage: StageInfo):
        embed = nextcord.Embed(title=f"Stage {stage.id}")
        embed.add_field(name="# Primary", value=stage.primary, inline=True)
        embed.add_field(name="# Secondary", value=stage.secondary, inline=False)
        # embed.add_field(name="​", value="​", inline=True)
        embed.add_field(name="Anomaly", value=str(stage.anomaly), inline=True)
        embed.add_field(name="Warning", value=str(stage.warning), inline=True)
        return embed

    def build(self, dd: DeepDiveInfo):
        embed_list = [self._buildMainEmbed(dd)]
        embed_list += [self._buildStageEmbed(stage) for stage in dd.stages]
        return embed_list


class DeepRockCog(commands.Cog):
    @nextcord.slash_command(name= "rawr", description="gets weekly deep dive information")
    async def deepdive(self, interaction: nextcord.Interaction):
        normal_dd, elite_dd = await DeepDiveManager().get_info()
        dde = DeepDiveEmbed()
        normal_embeds = dde.build(normal_dd)
        elite_embeds = dde.build(elite_dd)

        await interaction.send(embeds=normal_embeds)
        await interaction.send(embeds=elite_embeds)

