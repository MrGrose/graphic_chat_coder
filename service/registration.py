import asyncio
import json
import logging
import tkinter as tk
from tkinter import Label, Tk, messagebox

import aiofiles
from anyio import create_task_group
from draw.gui import TkAppClosed, update_tk
from environs import Env
from service.utils import create_parser, is_valid_nick

logger = logging.getLogger(__name__)


async def registration(host, port, nickname):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        await reader.readline()
        writer.write(b"\n")
        await writer.drain()
        await reader.readline()
        if nickname:
            writer.write(nickname.encode())
            await writer.drain()
        writer.write(b"\n")
        await writer.drain()
        data = await reader.readline()

        async with aiofiles.open("user_auth.txt", "w") as file:
            await file.write(data.decode().strip())

    finally:
        writer.close()
        await writer.wait_closed()

    return json.loads(data.decode().strip())


def process_registration(input_field, registration_queue):
    nick = input_field.get().strip()
    valid_nick = is_valid_nick(nick)
    if not valid_nick:
        messagebox.showwarning(
            "Внимание",
            "Никнейм должен содержать только анг. буквы и цифры (3-15 символов)."
        )
        return
    registration_queue.put_nowait(nick)
    input_field.delete(0, tk.END)


async def registration_worker(host, port, registration_queue):
    try:
        while True:
            nickname = await registration_queue.get()
            if nickname is None:
                break
            if data := await registration(host, port, nickname):
                messagebox.showinfo("Сообщение", "Ваш никнейм успешно создан, данные в файле user_auth.txt")
                raise TkAppClosed
    except Exception:
        raise


def on_close(root, registration_queue, cancel_scope):
    logger.info("Закрытие окна, отмена задачи")
    registration_queue.put_nowait(None)
    cancel_scope.cancel()
    root.destroy()


async def draw_registration():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    env = Env()
    env.read_env()

    parser = create_parser()
    args = parser.parse_args()

    host = args.host or env.str("HOST")
    port = args.send_port or env.int("SEND_PORT")

    registration_queue = asyncio.Queue()
    root = Tk()
    root.title("Регистрация")
    root.geometry("400x100")

    lbl = Label(root, text="Введине ваш ник")  
    lbl.pack(side="bottom")

    root_frame = tk.Frame()
    root_frame.pack(fill="both", expand=True)

    input_frame = tk.Frame(root_frame)
    input_frame.pack(side="bottom", fill=tk.X)

    input_field = tk.Entry(input_frame)
    input_field.pack(side="left", fill=tk.X, expand=True)

    send_button = tk.Button(input_frame)
    send_button["text"] = "Отправить"
    send_button["command"] = lambda: process_registration(input_field, registration_queue)
    send_button.pack(side="left")

    try:
        async with create_task_group() as tg:
            cancel_scope = tg.cancel_scope
            root.protocol("WM_DELETE_WINDOW", lambda: on_close(root, registration_queue, cancel_scope))
            tg.start_soon(update_tk, root_frame)
            tg.start_soon(registration_worker, host, port, registration_queue)

    except* TkAppClosed:
        logger.info("Приложение закрыто")
    except* (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        logger.info("Программа остановлена пользователем")
    except* Exception as e:
        logger.exception(f"Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(draw_registration())

