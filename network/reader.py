import asyncio
import datetime
from pathlib import Path

import aiofiles
from service.service import get_connection


async def read_msgs(host, port, messages_queue, save_queue, watchdog_queue, logger):
    while True:
        try:
            async with get_connection(host, port) as (reader, writer):
                while message := await reader.readline():
                    messages_queue.put_nowait(message.decode().strip())
                    await watchdog_queue.put("New message in chat")
                    await save_queue.put(message.decode().strip()) 
                break
        except ConnectionError as e:
            logger.error(f"Сетевая ошибка: {e}")
            await asyncio.sleep(5)


async def save_messages(folder_path, save_queue):
    folder = Path(__file__).parent.parent / folder_path
    folder.mkdir(exist_ok=True)
    file_path = folder / "data.txt"
    while message := await save_queue.get():
        formatted_date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        message = f"[{formatted_date}] {message}\n"
        async with aiofiles.open(file_path, "a", encoding="utf-8") as file:
            await file.write(message)
            save_queue.task_done()

    print(message, end="")
