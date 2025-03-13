#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
utils.py
Вспомогательные функции.

Содержит:
  - get_all_processes(): функция кроссплатформенного сбора информации о процессах
  - save_json(): функция сохранения данных в JSON
  - current_datetime_str(): генерация строки текущих даты/времени для имени файла
  - prepare_save_directory(): создание нужной структуры директорий
  - логирование
"""

import os
import platform
import subprocess
import json
from datetime import datetime


def get_all_processes():
    """
    Кроссплатформенная функция получения списка процессов.
    Возвращает список словарей:
      [
        {"pid": <int>, "name": <str>, "status": <str>, ...},
        ...
      ]
    Для Unix-подобных: используем 'ps -ef'
    Для Windows: используем 'tasklist'
    """
    processes = []

    system_name = platform.system().lower()
    try:
        if 'windows' in system_name:
            # Windows
            cmd = ["tasklist"]
            # Вывод:
            # Image Name                     PID Session Name        Session#    Mem Usage
            # ========================= ======== ================ =========== ============
            # System Idle Process              0 Services                   0         8 K
            output = subprocess.check_output(cmd, universal_newlines=True)
            lines = output.strip().split('\n')
            # Пропустим заголовок и разделители
            if len(lines) > 2:
                for line in lines[2:]:
                    parts = line.split()
                    # Формат содержит пробелы в названии Image Name, поэтому парсинг нетривиален
                    # PID - это второе "слово" в строке
                    if len(parts) >= 2:
                        pid_str = parts[-5]  # Ищем PID ориентируясь на "Session Name"
                        pid_str = parts[1] 
                        try:
                            pid = int(pid_str)
                        except ValueError:
                            continue
                        process_name = parts[0]
                        processes.append({
                            "pid": pid,
                            "name": process_name,
                            "status": "unknown"  # Windows tasklist напрямую статус не показывает
                        })
        else:
            # Unix-like
            cmd = ["ps", "-ef"]
            # Формат: UID        PID  PPID  C STIME TTY          TIME CMD
            output = subprocess.check_output(cmd, universal_newlines=True)
            lines = output.strip().split('\n')
            # Пропустим заголовок
            if len(lines) > 1:
                for line in lines[1:]:
                    parts = line.split(None, 7)  # Разбиваем по whitespace, максимум 8 полей
                    if len(parts) < 8:
                        continue
                    # parts[1] = PID, parts[2] = PPID, parts[7] = CMD
                    pid_str = parts[1]
                    cmd_str = parts[7]
                    try:
                        pid = int(pid_str)
                    except ValueError:
                        continue
                    processes.append({
                        "pid": pid,
                        "name": cmd_str,
                        "status": "running"
                    })
    except Exception as e:
        # Если возникла ошибка, возвращаем пустой список
        print(f"Ошибка при получении списка процессов: {e}")

    return processes


def save_json(data, filepath):
    """
    Сериализует data в JSON и сохраняет в указанный файл filepath.
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def current_datetime_str():
    """
    Возвращает пару:
      (date_str, time_str)
    где date_str = dd-mm-yyyy, time_str = hh:mm:ss
    Используется при формировании директорий/имён файлов.
    """
    now = datetime.now()
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%H-%M-%S")
    return date_str, time_str


def prepare_save_directory(base_dir, date_str):
    """
    Создаёт директорию base_dir/date_str, если её нет.
    Возвращает полный путь к этой директории.
    """
    full_path = os.path.join(base_dir, date_str)
    if not os.path.exists(full_path):
        os.makedirs(full_path, exist_ok=True)
    return full_path
