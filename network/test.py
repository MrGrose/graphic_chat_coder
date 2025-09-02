# import _tkinter
# import argparse
# import asyncio
# import datetime
# import json
# import logging
# import time
# import tkinter as tk
# from contextlib import asynccontextmanager
# from enum import Enum
# from pathlib import Path
# from tkinter import Button, Entry, Label, Text, Tk, messagebox
# from tkinter.scrolledtext import ScrolledText

# import aiofiles
# import graphic_chat_coder.draw.gui as gui
# from anyio import create_task_group
# from environs import Env

# # class ReadConnectionStateChanged(Enum):
# #     INITIATED = 'устанавливаем соединение'
# #     ESTABLISHED = 'соединение установлено'
# #     CLOSED = 'соединение закрыто'

# #     def __str__(self):
# #         return str(self.value)


# # class SendingConnectionStateChanged(Enum):
# #     INITIATED = 'устанавливаем соединение'
# #     ESTABLISHED = 'соединение установлено'
# #     CLOSED = 'соединение закрыто'

# #     def __str__(self):
# #         return str(self.value)
    
# # status_connect = {
# #     "New message in chat": ReadConnectionStateChanged.ESTABLISHED,
# #     "Message sent": SendingConnectionStateChanged.ESTABLISHED,
    
# # }

# # async def main():
# #     interval = 20
# #     while interval >= 0:
# #         async with asyncio.timeout(20) as cm:
# #             interval -= 1
# #             print(interval)
# #         if cm.expired:
# #             print(f"Прошло {interval} сек ")

# # asyncio.run(main())


# # =============================================================
# # async def simulate_status_updates(status_updates_queue):
# #     while True:
# #         for status in [gui.ReadConnectionStateChanged.ESTABLISHED,
# #                        gui.ReadConnectionStateChanged.INITIATED,
# #                        gui.ReadConnectionStateChanged.CLOSED]:
# #             await status_updates_queue.put(status)
# #             await asyncio.sleep(0.4)

# # status_connect = {
# #     "New message in chat": gui.ReadConnectionStateChanged.ESTABLISHED,
# #     "Message sent": gui.SendingConnectionStateChanged.ESTABLISHED,
    

# # def button_clicked():
# #     print (u"Клик!")
# # root=Tk()
# # # кнопка по умолчанию
# # button1 = Button()
# # button1.pack()
# # # кнопка с указанием родительского виджета и несколькими аргументами
# # button2 = Button(bg="red", text=u"Кликни меня!", command=button_clicked)
# # button2.pack()
# # root.mainloop()





# # def clicked():  
# #     res = txt.get()
# #     print(res)
# #     r = messagebox.askyesno("Ваш ник", res)
# #     # r = messagebox.showinfo("Ваш ник", res)
    
# #     # lbl.configure(text=res)
  
  
# # root = Tk()
# # root.title("Регистрация")  
# # # root.geometry('400x400')  
# # # lbl = Label(root, text="Привет")  
# # # lbl.grid(column=0, row=0)  
# # txt = Entry(root, width=40)  
# # # txt.grid(row=3, column=1)  
# # btn = Button(root, text="Регистрация", command=clicked)  
# # # btn.grid(column=2, row=0)

# # txt.pack()
# # btn.pack()  
  
# # root.mainloop()
# # def tk_registration(input_field):  
# #     res = input_field.get()
# #     print(res)
# #     # r = messagebox.askyesno("Ваш ник", res)
# #     # r = messagebox.showinfo("Ваш ник", res)
# #     input_field.delete(0, tk.END)
# #     return res

# class TkAppClosed(Exception):
#     pass




        
# async def registration(host, port, nickname, root):
#     # nickname = await sending_queue.get()

#     reader, writer = await asyncio.open_connection(host, port)
#     try:
#         data = await reader.readline()
#         # logger.debug(data.decode().strip())

#         writer.write(b"\n")
#         await writer.drain()

#         data = await reader.readline()
#         # logger.debug(data.decode().strip())

#         if nickname:
#             writer.write(nickname.encode())
#             await writer.drain()

#         writer.write(b"\n")
#         await writer.drain()

#         data = await reader.readline()
#         # logger.debug(f"Регистрация: {data.decode().strip()}")

#         async with aiofiles.open("user.txt", "w") as file:
#             await file.write(data.decode().strip())

#     finally:
#         writer.close()
#         await writer.wait_closed()
        
#     print(json.loads(data.decode().strip()))
    
#     return json.loads(data.decode().strip())


# import re


# def process_registration(input_field, root, sending_queue):
#     nick = input_field.get().strip()
#     valid_pattern = re.compile(r"^[a-zA-Z0-9]{3,15}$")
#     if not valid_pattern.match(nick):
#         messagebox.showwarning(
#             "Внимание",
#             "Никнейм должен содержать только буквы и цифры (3-15 символов)."
#         )
#         return
#     sending_queue.put_nowait(nick)
#     input_field.delete(0, tk.END)


# async def registration_worker(host, port, sending_queue, root):
#     while True:
#         nickname = await sending_queue.get()
#         if nickname is None:
#             break
#         try:
#             data = await registration(host, port, nickname, root)
#             if data:
#                 raise TkAppClosed
#         except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
#             # Задача отменена извне — выйти тихо
#             break


# async def update_tk(root_frame, interval=1 / 120):
#     while True:
#         try:
#             root_frame.update()
#         except tk.TclError:
#             raise TkAppClosed
#         await asyncio.sleep(interval)


# def on_close(root, sending_queue, task_group):
#     sending_queue.put_nowait(None)
#     root.destroy()
#     task_group.cancel_scope.cancel()


# async def reg():
#     sending_queue = asyncio.Queue()   
#     root = Tk()
#     root.title("Регистрация")
#     root.geometry("400x100")
#     root.protocol("WM_DELETE_WINDOW", lambda: on_close(root, sending_queue, tg))
#     lbl = Label(root, text="Введине ваш ник")  
#     lbl.pack(side="bottom")

#     root_frame = tk.Frame()
#     root_frame.pack(fill="both", expand=True)

#     input_frame = tk.Frame(root_frame)
#     input_frame.pack(side="bottom", fill=tk.X)

#     input_field = tk.Entry(input_frame)
#     input_field.pack(side="left", fill=tk.X, expand=True)

#     send_button = tk.Button(input_frame)
#     send_button["text"] = "Отправить"
#     send_button["command"] = lambda: process_registration(input_field, root, sending_queue)
#     send_button.pack(side="left")

#     try:
#         async with create_task_group() as tg:
#             tg.start_soon(update_tk, root_frame)
#             tg.start_soon(registration_worker, "minechat.dvmn.org", 5050, sending_queue, root)
#     except* (TkAppClosed, _tkinter.TclError):
#         root.destroy()
#         print("Приложение закрыто")
#     except* (KeyboardInterrupt, asyncio.exceptions.CancelledError):
#         # Задача отменена извне — выйти тихо
#         print("Программа остановлена пользователем")


# if __name__ == "__main__":
#     asyncio.run(reg())

from pathlib import Path

folder = Path(__file__).parent.parent
print(folder)