from typing import Protocol

class VoiceChatPasture(Protocol):
  async def speak_text(self, text: str) -> None:
    pass

class CowpanionPasture(Protocol):
  async def notify_user_joined(self, user: str) -> None:
    pass

  async def notify_user_left(self, user: str) -> None:
    pass
