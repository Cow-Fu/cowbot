import asyncio
import sys

import PySide6.QtAsyncio as QtAsyncio

from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

async def run_in_loop():
  while True:
    await asyncio.sleep(1)
    print('hi')

if __name__ == "__main__":
  app = QApplication()

  initial_view_path = Path(__file__).parent / 'App' / 'Main.qml'
  engine = QQmlApplicationEngine(str(initial_view_path))

  engine.quit.connect(QApplication.quit)

  QtAsyncio.run(run_in_loop(), handle_sigint = True)
