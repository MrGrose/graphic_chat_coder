import argparse
import re
from pathlib import Path


def create_parser():
    parser = argparse.ArgumentParser(description="Загрузка истории переписки из чата")
    parser.add_argument("--host", default="minechat.dvmn.org", help="host сервера")
    parser.add_argument("--read_port", default=5000, help="port для чтения сообщение")
    parser.add_argument("--send_port", default=5050, help="port для отправки сообщение")
    parser.add_argument("--history", default="minechat", help="Путь к файлу с историей переписки")
    parser.add_argument("--token", help="token пользователя")

    return parser


def is_valid_nick(nick):
    return bool(re.match(r"^[a-zA-Z0-9]{3,15}$", nick.strip()))
