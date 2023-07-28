from enum import Enum


class StrEnum(str, Enum):
    @classmethod
    def from_value(cls, value: str):
        return cls._value2member_map_[value]


class WarningEnum(StrEnum):
    CAVE_LEECH_CLUSTER = "Cave Leech Cluster"
    ELITE_THREAT = "Elite Threat"
    EXPLODER_INFESTATION = "Exploder Infestation"
    HAUNTED_CAVE = "Haunted Cave"
    LETHAL_ENEMIES = "Lethal Enemies"
    LITHOPHAGE_OUTBREAK = "Lithophage Outbreak"
    LOW_OXYGEN = "Low Oxygen"
    MACTERA_PLAGUE = "Mactera Plague"
    PARASITES = "Parasites"
    REGENERATIVE_BUGS = "Regenerative Bugs"
    RIVAL_PRESENCE = "Rival Presence"
    SHIELD_DISRUPTION = "Shield Disruption"
    SWARMAGEDDON = "Swarmageddon"

    __hazard_bonuses = {
        CAVE_LEECH_CLUSTER: 15,
        ELITE_THREAT: 30,
        EXPLODER_INFESTATION: 20,
        HAUNTED_CAVE: 30,
        LETHAL_ENEMIES: 25,
        LITHOPHAGE_OUTBREAK: 50,
        LOW_OXYGEN: 20,
        MACTERA_PLAGUE: 20,
        PARASITES: 15,
        REGENERATIVE_BUGS: 15,
        RIVAL_PRESENCE: 30,
        SHIELD_DISRUPTION: 30,
        SWARMAGEDDON: 20
    }

    def get_hazard_modifier(self):
        return self.__hazard_bonuses[self]


class MutatorEnum(StrEnum):
    CRITICAL_WEAKNESS = "Critical Weakness"
    DOUBLE_XP = "Double XP"
    GOLD_RUSH = "Gold Rush"
    GOLDEN_BUGS = "Golden Bugs"
    LOW_GRAVITY = "Low Gravity"
    MINERAL_MANIA = "Mineral Mania"
    RICH_ATMOSPHERE = "Rich Atmosphere"
    VOLATILE_GUTS = "Volatile Guts"


class MissionTypeEnum(StrEnum):
    MINING_EXPEDITION = "Mining Expedition"
    EGG_HUNT = "Egg Hunt"
    ON_SITE_REFINING = "On-site Refining"
    SALVAGE_OPERATION = "Salvage Operation"
    POINT_EXTRACTION = "Point Extraction"
    ESCORT_DUTY = "Escort Duty"
    ELIMINATION = "Elimination"
    INDUSTRIAL_SABOTAGE = "Industrial Sabotage"


class BiomeEnum(StrEnum):
    AZURE_WEALD = "Azure Weald"
    CRYSTALLINE_CAVERNS = "Crystalline Caverns"
    DENSE_BIOZONE = "Dense Biozone"
    FUNGUS_BOGS = "Fungus Bogs"
    GLACIAL_STRATA = "Glacial Strata"
    HOLLOW_BOUGH = "Hollow Bough"
    MAGMA_CORE = "Magma Core"
    RADIOACTIVE_EXCLUSION_ZONE = "Radioactive Exclusion Zone"
    SALT_PITS = "Salt Pits"
    SANDBLASTED_CORRIDORS = "Sandblasted Corridors"


class SecondaryObjectiveEnum(StrEnum):
    APOCABLOOMS = "ApocaBlooms"
    BOOLO_CAPS = "Boolo Caps"
    DYSTRUM = "Dystrum"
    EBONUTS = "Ebonuts"
    FESTER_FLEAS = "Fester Fleas"
    FOSSILS = "Fossils"
    GUNK_SEEDS = "Gunk Seeds"
    HOLLOMITE = "Hollomite"
