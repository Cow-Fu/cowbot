
from enum import Enum

class VoiceStateChangeType(Enum):
    JOIN = "JOIN",
    LEAVE = "LEAVE",
    SWAP = "SWAP",
    MUTE = "MUTE",
    DEAFEN = "DEAFEN"