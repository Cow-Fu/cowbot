
from enum import Enum

class VoiceStateChangeType(Enum):
    JOIN = "JOIN",
    LEAVE = "LEAVE",
    SWAP = "SWAP",
    MUTE = "MUTE",
    DEAFEN = "DEAFEN",
    UNMUTE = "UNMUTE",
    UNDEAFEN = "UNDEAFEN"
    JOIN_MUTED = "JOIN_MUTED",
    JOIN_DEAFENED = "JOIN_DEAFENED",
    LEAVE_MUTED = "LEAVE_MUTED",
    LEAVE_DEAFENED = "LEAVE_MUTED"

