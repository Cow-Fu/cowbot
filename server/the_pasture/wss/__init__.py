import asyncio
import functools
import json

from websockets.exceptions import ConnectionClosed
from websockets.asyncio.router import route
from websockets.asyncio.server import ServerConnection, broadcast
from werkzeug.routing import Map, Rule

from the_pasture.protocol import VoiceChatPasture

class WebSocketPasture:
  def __init__(self) -> None:
    self.voice_chat_bot = None
    self.client_sockets = []

  def set_voice_bot(self, voice_chat_bot: VoiceChatPasture) -> None:
    self.voice_chat_bot = voice_chat_bot

  async def _handle_client_incoming(self, socket: ServerConnection) -> None:
    async for message in socket:
      print(f"Incoming message received: {message}")

  async def _handle_client_outgoing(self, socket: ServerConnection) -> None:
    while True:
      await socket.send('Hi from the server')
      await asyncio.sleep(5)

  async def _client_connection(self, socket: ServerConnection) -> None:
    try:
      print('Connection to client started.')
      self.client_sockets.append(socket)
      # Sends a message to all clients.
      broadcast(self.client_sockets, 'New client connected!')
      await asyncio.gather(
        self._handle_client_incoming(socket),
        self._handle_client_outgoing(socket)
      )
    except ConnectionClosed:
      print('Connection to client closed.')
    finally:
      self.client_sockets.remove(socket)

  async def run() -> None:
    url_map = Map([
        Rule(
          '/client/',
          endpoint = functools.patrial(self._client_connection, self)
        ),
    ])
    async with route(url_map, port = 8523) as server:
      await server.serve_forever()

  async def notify_user_joined(self, user: str) -> None:
    broadcast(
      self.client_sockets,
      json.dumps({'t': 'user-join', 'v': user})
    )

  async def notify_user_left(self, user: str) -> None:
    broadcast(
      self.client_sockets,
      json.dumps({'t': 'user-leave', 'v': user})
    )

