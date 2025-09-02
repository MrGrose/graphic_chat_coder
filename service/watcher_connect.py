import asyncio
import logging
import time
from pathlib import Path

import draw.gui as gui

logger_dir = Path("logger_files")
logger_dir.mkdir(exist_ok=True)

watchdog_logger = logging.getLogger("watchdog")
watchdog_file_handler = logging.FileHandler(logger_dir / "watch_log.txt")
watchdog_file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
watchdog_file_handler.setFormatter(formatter)

watchdog_logger.addHandler(watchdog_file_handler)
watchdog_logger.propagate = False 

async def watch_for_connection(watchdog_queue, status_updates_queue):
    while True:
        try:
            async with asyncio.timeout(3):
                message = await watchdog_queue.get()
                await status_updates_queue.put(gui.ReadConnectionStateChanged.ESTABLISHED)
                await status_updates_queue.put(gui.SendingConnectionStateChanged.ESTABLISHED)
                watchdog_logger.info(f"[{time.time():.0f}] Connection is alive. Source: {message}")

        except asyncio.TimeoutError:
            await status_updates_queue.put(gui.ReadConnectionStateChanged.INITIATED)
            await status_updates_queue.put(gui.SendingConnectionStateChanged.INITIATED)
            watchdog_logger.info(f"[{time.time():.0f}] 1s timeout is elapsed")
            raise ConnectionError