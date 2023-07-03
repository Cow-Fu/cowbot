import nextcord
from nextcord.ext import commands
from requests import get
import json
from dataclasses import dataclass
from typing import List, Optional
import asyncio
from abc import ABC, abstractmethod
import table2ascii as t2a


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


class DeepDiveDisplayBuilder(ABC):
    @abstractmethod
    def build(self, dd: DeepDiveInfo):
        pass


class DeepDiveTextBuilder(DeepDiveDisplayBuilder):
    def build(self, dd: DeepDiveInfo):
        header = [dd.type, t2a.Merge.LEFT]
        body = []
        body.append(["Code Name", dd.name])
        body.append(["Biome", dd.biome])
        for stage in dd.stages:
            body.append([" ", " "])
            body.append([f"Stage {stage.id}", t2a.Merge.LEFT])
            body.append(["Primary", stage.primary])
            body.append(["Secondary", stage.secondary])
            body.append(["Anomaly", stage.anomaly])
            body.append(["Warning", stage.warning])

        return t2a.table2ascii(
                header=header,
                body=body,
                style=t2a.PresetStyle.thin_compact_rounded
                )


class DeepDiveEmbedBuilder(DeepDiveDisplayBuilder):
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
    @nextcord.slash_command(name="deepdive", description="gets weekly deep dive information")
    async def deepdive(self, interaction: nextcord.Interaction, choice: int = nextcord.SlashOption(
            name="type",
            description="Select if you want regular or elite deep dive information",
            choices={"Normal": 0, "Elite": 1, "Both": 2}
    )):
        normal_dd, elite_dd = await DeepDiveManager().get_info()
        ddb = DeepDiveTextBuilder()
        info = []

        if choice == 0 or choice == 2:
            info.append(ddb.build(normal_dd))
        if choice == 1 or choice == 2:
            info.append(ddb.build(elite_dd))
        embeds = []
        for item in info:
            embeds.append(nextcord.Embed(description=f"```{item}```"))

        await interaction.send(embeds=embeds)
