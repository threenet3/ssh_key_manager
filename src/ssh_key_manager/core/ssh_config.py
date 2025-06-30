import os
from pathlib import Path
from typing import List, Dict, Optional

# путь к ssh конигу текущего пользователя
CONFIG_PATH = Path.home() / ".ssh" / "config"

"""
Читаем ~/.ssh/config и возвращаем список хостов с параметрами

Пример [{'Host': 'github.com', 'IdentityFile': '~/.ssh/id_ed25519'}]
"""
def read_config() -> List[Dict[str, str]]:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(mode=0o700, exist_ok=True)
        CONFIG_PATH.touch(mode=0o600, exist_ok=True)
        return []

    config_entries = []
    current_entry = {}

    with CONFIG_PATH.open("r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.lower().startswith("host "):
                if current_entry:
                    config_entries.append(current_entry)
                current_entry = {"Host": line.split(maxsplit=1)[1]}
            else:
                if current_entry:
                    parts = line.split(maxsplit=1)
                    if len(parts) == 2:
                        current_entry[parts[0]] = parts[1]

        if current_entry:
            config_entries.append(current_entry)

    return config_entries


"""
Перезаписывает ~/.ssh/config на основе предоставленного списка словарей
каждый словарь соответствует одному блоку хоста
"""
def write_config(entries: List[Dict[str, str]]) -> None:
    lines = []
    for entry in entries:
        lines.append(f"Host {entry.get('Host')}") # заголовок
        for k, v in entry.items():
            if k != "Host":
                lines.append(f"    {k} {v}") # параметры блока (отступ + ключ + значение)
        lines.append("")  # пустая строка между блоками

    CONFIG_PATH.parent.mkdir(mode=0o700, exist_ok=True) # проверка на права и существование
    CONFIG_PATH.write_text("\n".join(lines), encoding="utf-8") # запись в файл

"""
Добавляет или обновляет запись по 'Host'
"""
def add_or_update_host(new_entry: Dict[str, str]) -> None:
    entries = read_config()
    updated = False

    for i, entry in enumerate(entries):
        if entry.get("Host") == new_entry.get("Host"):
            entries[i] = new_entry # обновляем запись
            updated = True
            break

    if not updated:
        entries.append(new_entry) # новая запись

    write_config(entries)

"""
Удаляет запись с указанным Host

Читаем конфигурацию, создаем новый список без удаляемого хоста, 
а затем записываем обновленный
"""
def delete_host(host_name: str) -> bool:
    entries = read_config()
    new_entries = [e for e in entries if e.get("Host") != host_name]

    if len(new_entries) == len(entries):
        return False  # не найдено

    write_config(new_entries)
    return True


"""
Возвращает словарь параметров для заданного Host, если найден
то как словарь, если не найден то None
"""
def get_host_entry(host_name: str) -> Optional[Dict[str, str]]:
    for entry in read_config():
        if entry.get("Host") == host_name:
            return entry
    return None
