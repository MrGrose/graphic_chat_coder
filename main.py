import asyncio
import logging
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

import draw.gui as gui
from anyio import create_task_group
from environs import Env
from network.reader import read_msgs, save_messages
from network.sender import send_msgs
from service.authorise import InvalidToken, authorise
from service.service import load_history_chat, send_keep_alive
from service.utils import create_parser
from service.watcher_connect import watch_for_connection, watchdog_logger

logger = logging.getLogger(__name__)


async def handle_connection(messages_queue, sending_queue, status_updates_queue, save_queue, watchdog_queue, host, read_port, send_port, history, token, logger):
    while True:
        try:
            async with create_task_group() as tg:
                tg.start_soon(save_messages, history, save_queue)
                tg.start_soon(read_msgs, host, read_port, messages_queue, save_queue, watchdog_queue, logger)
                tg.start_soon(send_msgs, host, send_port, token, sending_queue, watchdog_queue, logger)
                tg.start_soon(watch_for_connection, watchdog_queue, status_updates_queue)
                tg.start_soon(send_keep_alive, host, send_port)

        except* ConnectionError:
            await status_updates_queue.put(gui.ReadConnectionStateChanged.CLOSED)
            await status_updates_queue.put(gui.SendingConnectionStateChanged.CLOSED)
            watchdog_logger.info(f"[{time.time():.0f}] Connection error, restarting")
            await asyncio.sleep(0.4)


async def main():
    env = Env()
    env.read_env()
    
    logger_dir = Path("logger_files")
    logger_dir.mkdir(exist_ok=True)

    logging.basicConfig(filename=logger_dir/"main_log.txt", format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)

    parser = create_parser()
    args = parser.parse_args()
    host = args.host or env.str("HOST")
    read_port = args.read_port or env.int("READ_PORT")
    send_port = args.send_port or env.int("SEND_PORT")
    history = args.history or env.str("HISTORY")
    token = args.token or env.str("USER_TOKEN", None)

    messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()
    save_queue = asyncio.Queue()
    watchdog_queue = asyncio.Queue()

    await load_history_chat(history, messages_queue)

    try:
        if not token:
            messagebox.showinfo("Ошибка", "Токен не обнаружен, проверьте или пройдите регистрацию")
            raise InvalidToken

        is_authorized = await authorise(host, send_port, token, messages_queue, status_updates_queue, watchdog_queue, logger)
        if not is_authorized:
            raise
        else:
            logger.info("Запуск корутин")
            async with create_task_group() as tg:
                tg.start_soon(handle_connection, messages_queue, sending_queue, status_updates_queue, save_queue, watchdog_queue, host, read_port, send_port, history, token, logger)
                tg.start_soon(gui.draw, messages_queue, sending_queue, status_updates_queue)

    except* (gui.TkAppClosed, tk.TclError):
        logger.info("Приложение закрыто")
    except* InvalidToken:
        logger.error("Не верный token")
    except* (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        logger.info("Программа остановлена пользователем")
    except* Exception as e:
        logger.exception(f"Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())