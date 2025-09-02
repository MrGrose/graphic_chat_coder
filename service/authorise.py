import json
from tkinter import messagebox

import draw.gui as gui
# from main import logger
from service.service import get_connection


class InvalidToken(Exception):
    pass


async def authorise(host, port, token, messages_queue, status_updates_queue, watchdog_queue, logger):
    async with get_connection(host, port) as (reader, writer):

        data = await reader.readline()
        logger.debug(data.decode().strip())

        writer.write(token.encode() + b"\n")
        logger.debug(f"Проверка token: {token}")
        await writer.drain()
        data = await reader.readline()
        logger.debug(f"Полученные данные: {data.decode().strip()}")

        try:
            user_info = json.loads(data.decode().strip())
            if user_info is None:
                messagebox.showinfo("Не верный token", "Проверьте token, сервер его не узнал")
                raise InvalidToken

            watchdog_queue.put_nowait("Authorization done")
            messages_queue.put_nowait(f"Выполнена авторизация. Пользователь {user_info["nickname"]}")
            status_updates_queue.put_nowait(gui.NicknameReceived(user_info["nickname"]))

            return user_info
        except json.JSONDecodeError:
            raise
