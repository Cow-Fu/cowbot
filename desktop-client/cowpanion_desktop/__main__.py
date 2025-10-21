import asyncio
import sys

import PySide6.QtCore as QtCore
import PySide6.QtAsyncio as QtAsyncio

from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

from cowpanion_desktop import rc_icons

async def run_in_loop():
  while True:
    await asyncio.sleep(1)
    print('hi')

if __name__ == "__main__":
  app = QApplication()

  script_dir_path = Path(__file__).parent
  initial_view_path = script_dir_path / 'App' / 'Main.qml'
  engine = QQmlApplicationEngine(str(initial_view_path))

  app.setWindowIcon(QIcon(":/icons/tray.png"));

  engine.quit.connect(QApplication.quit)

  QtAsyncio.run(run_in_loop(), handle_sigint = True)
