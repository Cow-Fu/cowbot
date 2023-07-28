import json
from datetime import datetime
from dateutil import tz
from typing import List, Optional
from dataclasses import dataclass
from DeepRockEnums import MutatorEnum, WarningEnum, BiomeEnum
from requests import get


@dataclass(slots=True)
class ObjectiveData:
    code_name: str
    complexity: int
    length: int
    mission_mutator: Optional[MutatorEnum]
    mission_warnings: Optional[List[WarningEnum]]
    primary: str
    secondary: str
    id: int


@dataclass(slots=True)
class BiomeData:
    biome: BiomeEnum
    objectives: List[ObjectiveData]


@dataclass(slots=True)
class MissionData:
    biomes: List[BiomeData]
    time: datetime


class MissionBuilder:
    @staticmethod
    def objective_builder(item: dict):
        mutator = None
        warnings = None
        if "MissionMutator" in item:
            MutatorEnum._value2member_map_
            mutator = MutatorEnum.from_value(item["MissionMutator"])
        if "MissionWarnings" in item:
            warnings = [WarningEnum.from_value(warn) for warn in item["MissionWarnings"]]

        return ObjectiveData(
                code_name=item["CodeName"],
                complexity=int(item["Complexity"]),
                length=int(item["Length"]),
                mission_mutator=mutator,
                mission_warnings=warnings,
                primary=item["PrimaryObjective"],
                secondary=item["SecondaryObjective"],
                id=item["id"]
            )

    @staticmethod
    def biome_builder(name: str, mission_list: list):
        return BiomeData(
                biome=BiomeEnum.from_value(name),
                objectives=[MissionBuilder.objective_builder(mission) for mission in mission_list]
                )

    def _convert_from_utc_to_est(utc: datetime):
        from_zone = tz.tzutc()
        to_zone = tz.gettz("America/New_York")
        utc = utc.replace(tzinfo=from_zone)
        return utc.astimezone(to_zone)

    @staticmethod
    def mission_data_builder(mission_data: dict):
        utc = datetime.fromisoformat(mission_data["timestamp"][0:-1])
        eastern = MissionBuilder._convert_from_utc_to_est(utc)
        return MissionData(
            biomes=[MissionBuilder.biome_builder(name, mlist) for name, mlist in mission_data["Biomes"].items()],
            time=eastern
        )

    @staticmethod
    def time_until_next(dt: datetime):
        now = datetime.now()
        current_minute = now.time().minute
        minute_diff = current_minute - dt.time().minute
        return 30 - minute_diff

if __name__ == "__main__":
    current_data = get("https://doublexp.net/json?data=current").content
    current_data = json.loads(current_data)
    current_missions = MissionBuilder.mission_data_builder(current_data)
    secondary = set()
    for biome in current_missions.biomes:
        for objective in biome.objectives:
            secondary.add(objective.secondary)
    print(secondary)
            
#
# print(f"Minutes until next mission: {time_until_next(current_missions.time)}")
# upcoming_data = get("https://doublexp.net/json?data=next").content
# upcoming_data = json.loads(upcoming_data)
# upcoming_missions = mission_data_builder(upcoming_data)
# print(current_missions)
