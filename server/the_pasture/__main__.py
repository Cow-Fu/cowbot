import asyncio
import os

from dotenv import load_dotenv

# Pull in submodules
from the_pasture.discord import DiscordPasture
from the_pasture.wss import WebSocketPasture

async def main() -> None:
  # Load the environment information from the .env file.
  load_dotenv()

  # Construct the two services.
  discord_past = DiscordPasture()
  ws_past = WebSocketPasture()

  # Notify them of each other.
  discord_past.set_cowpanion_wss(ws_past)
  ws_past.set_voice_bot(discord_past)

  # Run services forever...
  await asyncio.gather(
    discord_past.run(os.getenv('BOT_TOKEN')),
    ws_past.run()
  )

asyncio.run(main())
