#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import socket
import logging
import struct

from utils import prepare_save_directory, current_datetime_str

HOST = "127.0.0.1"
PORT = 9000

logging.basicConfig(
    filename='client_log.txt',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def run_client():
    logging.info("Клиент запускается...")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cli_socket:
            cli_socket.connect((HOST, PORT))
            logging.info(f"Подключение к {HOST}:{PORT} установлено.")

            welcome = cli_socket.recv(1024).decode('utf-8', errors='ignore')
            logging.info(f"Сообщение от сервера: {welcome.strip()}")

            while True:
                command = input("Введите команду (update / kill / exit): ").strip()
                if not command:
                    continue

                # Отправляем команду
                cli_socket.sendall(command.encode('utf-8'))

                if command.lower() == "exit":
                    # После этого сервер завершит работу, клиент - тоже
                    logging.info("Отправлена команда 'exit' - завершаем работу клиента.")
                    # Дожидаемся короткого ответа от сервера
                    try:
                        resp = cli_socket.recv(1024)
                        if resp:
                            print(resp.decode('utf-8', errors='ignore'))
                    except:
                        pass
                    break

                elif command == "update":
                    # Получаем 8 байт (размер файла)
                    size_data = recv_exact_bytes(cli_socket, 8)
                    if not size_data:
                        print("Сервер не прислал размер файла (или соединение закрыто).")
                        logging.warning("Не удалось получить размер файла от сервера.")
                        break

                    file_size = struct.unpack('>Q', size_data)[0]
                    if file_size == 0:
                        print("Сервер прислал пустой файл или ошибку.")
                        logging.warning("Получен размер файла 0 байт.")
                        continue

                    file_bytes = recv_exact_bytes(cli_socket, file_size)
                    if not file_bytes:
                        print("Не удалось получить содержимое файла полностью.")
                        logging.warning("Получено недостаточно байт файла.")
                        break

                    date_str, time_str = current_datetime_str()
                    save_dir = prepare_save_directory(".", date_str)
                    out_filename = f"{time_str}.json"
                    out_path = os.path.join(save_dir, out_filename)

                    with open(out_path, 'wb') as f:
                        f.write(file_bytes)

                    logging.info(f"Файл с процессами (size={file_size}) сохранён: {out_path}")
                    print(f"Файл обновлённой информации сохранён: {out_path}")

                elif command.startswith("kill"):
                    resp = cli_socket.recv(1024)
                    if resp:
                        print(resp.decode('utf-8', errors='ignore'))
                    else:
                        print("Нет ответа от сервера на команду kill.")

                else:
                    # Любая другая команда - получим ответ
                    resp = cli_socket.recv(1024)
                    if resp:
                        print(resp.decode('utf-8', errors='ignore'))
                    else:
                        print("Нет ответа от сервера на неизвестную команду.")

    except ConnectionRefusedError:
        logging.error(f"Сервер {HOST}:{PORT} недоступен (ConnectionRefusedError).")
        print(f"Ошибка: сервер {HOST}:{PORT} недоступен.")
    except KeyboardInterrupt:
        logging.info("Клиент остановлен (KeyboardInterrupt).")
    except Exception as e:
        logging.error(f"Ошибка в работе клиента: {e}")
        print(f"Ошибка клиента: {e}")

def recv_exact_bytes(sock, num_bytes):
    """
    Считывает ровно num_bytes байт из сокета.
    Если не удаётся прочитать нужный объём (сокет закрылся), возвращает None.
    """
    data = b""
    while len(data) < num_bytes:
        chunk = sock.recv(num_bytes - len(data))
        if not chunk:
            return None
        data += chunk
    return data
