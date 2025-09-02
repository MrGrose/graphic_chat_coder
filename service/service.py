import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

import aiofiles


@asynccontextmanager
async def get_connection(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()


async def send_keep_alive(host, port):
    interval = 30
    async with get_connection(host, port) as (reader, writer):
        while True:
            await asyncio.sleep(interval)
            writer.write(b"")
            await writer.drain()
            data = await reader.readline()
            if not data:
                raise ConnectionError


async def load_history_chat(folder_path, messages_queue):
    folder = Path(folder_path)
    file_path = folder / "data.txt"
    if not file_path.exists():
        return
    async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
        async for message in file:
            await messages_queue.put(message.strip())