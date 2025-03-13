#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main.py
Главная точка входа в приложение 1lab.

Запуск сервера:
    python3 main.py server

Запуск клиента:
    python3 main.py client
"""

import sys
from server import run_server
from client import run_client


def main():
    if len(sys.argv) < 2:
        print("Использование:\n  python3 main.py [server|client]")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "server":
        run_server()
    elif mode == "client":
        run_client()
    else:
        print(f"Неизвестный режим: '{mode}'. Ожидается 'server' или 'client'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
