import os
from pathlib import Path
from typing import List, Dict, Optional, Union

# путь к ssh конигу текущего пользователя
CONFIG_PATH = Path.home() / ".ssh" / "config"

# Для определения блоков для глобальных строк (доп. настройки), для хостов с параметрами
Block = Dict[str, Union[str, List[str], Dict[str, str]]]


"""
Читает ~/.ssh/config и возвращает список блоков в исходном порядке

Каждый блок, либо:
- строки вне блоков Host, сохраняющие порядок и комментарии,
- блок Host с параметрами

Позволяет сохранить произвольный порядок блоков и смешанные настройки

Возвращает List[Block] - список блоков с их содержимым
"""
def read_config() -> List[Block]:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(mode=0o700, exist_ok=True)
        CONFIG_PATH.touch(mode=0o600, exist_ok=True)
        return []

    blocks: List[Block] = []
    current_block: Optional[Block] = None

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped.lower().startswith("host "):
                # новый блок host
                if current_block:
                    blocks.append(current_block)
                host_name = stripped.split(maxsplit=1)[1]
                current_block = {
                    "type": "host",
                    "host": host_name,
                    "lines": [line],
                    "params": {}
                }
            else:
                if current_block is None or current_block["type"] == "global":
                    # продолжаем или создаём глобальный блок
                    if current_block is None:
                        current_block = {"type": "global", "lines": []}
                    if stripped and not stripped.startswith("#"):
                        parts = stripped.split(maxsplit=1)
                        if len(parts) == 2:
                            current_block.setdefault("params", {})[parts[0]] = parts[1]
                    current_block["lines"].append(line)
                else:
                    # в блоке host, но строка не "Host" — параметры или комментарии
                    current_block["lines"].append(line)
                    if stripped and not stripped.startswith("#"):
                        parts = stripped.split(maxsplit=1)
                        if len(parts) == 2:
                            current_block["params"][parts[0]] = parts[1]

        # добавить последний блок
        if current_block:
            blocks.append(current_block)

    return blocks


"""
Перезаписывает ~/.ssh/config на основе списка блоков

Сохраняет исходные строки, порядок и комментарии, 
добавляя пустую строку между блоками
"""
def write_config(blocks: List[Block]) -> None:
    lines = []
    for block in blocks:
        lines.extend(block["lines"])
        # проверка, что между блоками есть пустая строка
        if not block["lines"][-1].endswith("\n"):
            lines.append("\n") # добавляем пустую строку
    CONFIG_PATH.parent.mkdir(mode=0o700, exist_ok=True)
    CONFIG_PATH.write_text("".join(lines), encoding="utf-8")



"""
Добавляет новый блок Host или обновляет существующий по ключу 'Host'

Если блок с таким Host уже есть, то его содержимое обновляется, иначе
новый блок добавляется в конец файла

При обновлении исходные строки блока заменяются на новые, сформированные
из переданного словаря new_entry
"""
def add_or_update_host(new_entry: Dict[str, str]) -> None:
    blocks = read_config()
    host_name = new_entry.get("Host")
    updated = False

    for block in blocks:
        if block["type"] == "host" and block.get("host") == host_name:
            # Обновляем блок, делаем новые строки из new_entry
            new_lines = [f"Host {host_name}\n"]
            for k, v in new_entry.items():
                if k != "Host":
                    new_lines.append(f"    {k} {v}\n")
            block["lines"] = new_lines
            block["params"] = {k: v for k, v in new_entry.items() if k != "Host"}
            updated = True
            break

    if not updated:
        # Добавляем новый блок в конец
        new_lines = [f"Host {host_name}\n"]
        for k, v in new_entry.items():
            if k != "Host":
                new_lines.append(f"    {k} {v}\n")
        blocks.append({
            "type": "host",
            "host": host_name,
            "lines": new_lines,
            "params": {k: v for k, v in new_entry.items() if k != "Host"},
        })

    write_config(blocks)


"""
Удаляет блок Host с указанным именем

Возвращает True, если блок был найден и удалён, иначе False
"""
def delete_host(host_name: str) -> bool:
    blocks = read_config()
    new_blocks = [b for b in blocks if not (b["type"] == "host" and b.get("host") == host_name)]

    if len(new_blocks) == len(blocks):
        return False

    write_config(new_blocks)
    return True


"""
Возвращает словарь параметров для указанного Host, 
если блок найден, иначе None
"""
def get_host_entry(host_name: str) -> Optional[Dict[str, str]]:
    blocks = read_config()
    for block in blocks:
        if block["type"] == "host" and block.get("host") == host_name:
            entry = {"Host": host_name}
            entry.update(block.get("params", {}))
            return entry
    return None
