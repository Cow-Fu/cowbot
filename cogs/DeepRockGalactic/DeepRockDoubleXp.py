from DeepRockMissionObjects import MissionData
from DeepRockEnums import MutatorEnum


class DeepRockDoubleXpChecker:
    def check_if_double_xp(self, missions: MissionData) -> None:
        result = {}
        for biome in missions.biomes:
            for objective in biome.objectives:
                if objective.mission_mutator == MutatorEnum.DOUBLE_XP:
                    if biome.biome not in result:
                        result[biome.biome] = []
                    result[biome.biome].append(objective)
        return result
                
