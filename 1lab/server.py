#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import socket
import logging
import struct
from datetime import datetime

from utils import get_all_processes, save_json

HOST = "127.0.0.1"
PORT = 9000

logging.basicConfig(
    filename='server_log.txt',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def run_server():
    """
    Запуск сервера в цикле (блокирующий).
    Принимает подключения и создаёт обработку клиента.
    Если handle_client вернёт True, значит нужно остановить сервер.
    """
    logging.info("Сервер запускается...")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv_socket:
            srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv_socket.bind((HOST, PORT))
            srv_socket.listen(5)

            logging.info(f"Сервер слушает на {HOST}:{PORT}")

            while True:
                client_sock, client_addr = srv_socket.accept()
                logging.info(f"Подключился клиент: {client_addr}")
                
                # handle_client вернёт True, если нужно завершить сервер
                should_stop = handle_client(client_sock, client_addr)
                
                if should_stop:
                    logging.info("Получена команда 'exit' - завершаем сервер.")
                    break

    except KeyboardInterrupt:
        logging.info("Сервер остановлен (KeyboardInterrupt)")
    except Exception as e:
        logging.error(f"Ошибка в работе сервера: {e}")

def handle_client(client_sock, client_addr):
    """
    Обработка команд от одного клиента в рамках подключённого сокета.
    Возвращает True, если сервер должен завершиться (команда 'exit').
    """
    with client_sock:
        # Приветственное сообщение
        client_sock.sendall("CONNECTED\n".encode('utf-8'))

        while True:
            try:
                data = client_sock.recv(1024)
                if not data:
                    logging.info(f"Клиент {client_addr} разорвал соединение.")
                    break

                command = data.decode('utf-8', errors='ignore').strip()
                logging.info(f"Получена команда от {client_addr}: '{command}'")

                if command == "exit":
                    # Со стороны клиента это значит завершить и клиент, и сервер
                    logging.info(f"Клиент {client_addr} попросил завершить работу сервера.")
                    # Отвечаем клиенту:
                    client_sock.sendall("Сервер завершается.\n".encode('utf-8'))
                    return True  # Вернём True -> прерываем главный цикл сервера

                elif command == "update":
                    # Сформировать новый файл с процессами, отправить
                    json_file = create_processes_file()
                    send_file_to_client(client_sock, json_file)

                elif command.startswith("kill"):
                    # Формат: kill <pid> <signal>
                    parts = command.split()
                    if len(parts) == 3:
                        pid_str, sig_str = parts[1], parts[2]
                        try:
                            pid = int(pid_str)
                            sig = int(sig_str)
                            os.kill(pid, sig)
                            msg = f"OK: Сигнал={sig} отправлен процессу {pid}\n"
                            logging.info(msg.strip())
                            client_sock.sendall(msg.encode('utf-8'))
                        except ProcessLookupError:
                            err = f"ERROR: Процесс {pid_str} не найден\n"
                            logging.error(err.strip())
                            client_sock.sendall(err.encode('utf-8'))
                        except PermissionError:
                            err = f"ERROR: Нет прав для сигнала процессу {pid_str}\n"
                            logging.error(err.strip())
                            client_sock.sendall(err.encode('utf-8'))
                        except ValueError:
                            err = "ERROR: Некорректный формат PID или SIG\n"
                            logging.error(err.strip())
                            client_sock.sendall(err.encode('utf-8'))
                        except Exception as e:
                            err = f"ERROR: Невозможно послать сигнал: {e}\n"
                            logging.error(err.strip())
                            client_sock.sendall(err.encode('utf-8'))
                    else:
                        err = "ERROR: Формат команды kill - 'kill <pid> <signal>'\n"
                        logging.error(err.strip())
                        client_sock.sendall(err.encode('utf-8'))

                else:
                    msg = f"ERROR: Неизвестная команда '{command}'\n"
                    logging.warning(msg.strip())
                    client_sock.sendall(msg.encode('utf-8'))

            except ConnectionResetError:
                logging.warning(f"Клиент {client_addr} аварийно прервал соединение.")
                break
            except Exception as e:
                logging.error(f"Ошибка при обмене с клиентом {client_addr}: {e}")
                break

    logging.info(f"Сеанс с клиентом {client_addr} завершён.")
    return False  # Не прерываем сервер, если команду exit не прислали

def create_processes_file():
    from utils import get_all_processes, save_json
    processes = get_all_processes()
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"processes_{timestamp_str}.json"
    save_json(processes, filename)

    logging.info(f"Сохранён файл с информацией о процессах: {filename}")
    return filename

def send_file_to_client(client_sock, filepath):
    """
    Отправляет файл клиенту, используя struct для длины.
    Формат: [8 байт длины][байты файла]
    """
    try:
        with open(filepath, 'rb') as f:
            file_bytes = f.read()

        file_size = len(file_bytes)
        import struct
        packed_size = struct.pack('>Q', file_size)  # big-endian на 8 байт

        client_sock.sendall(packed_size)
        client_sock.sendall(file_bytes)

        logging.info(f"Файл {filepath} ({file_size} байт) отправлен клиенту.")
    except FileNotFoundError:
        err = f"ERROR: Файл {filepath} не найден\n"
        logging.error(err.strip())
        client_sock.sendall(err.encode('utf-8'))
    except Exception as e:
        err = f"ERROR: Не удалось отправить файл {filepath}. Причина: {e}\n"
        logging.error(err.strip())
        client_sock.sendall(err.encode('utf-8'))
