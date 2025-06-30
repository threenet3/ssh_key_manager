import re
import os
from pathlib import Path

SSH_DIR = Path.home() / ".ssh"

KEY_NAME_REGEX = re.compile(r'^[a-zA-Z0-9_\-\.]+$')
HOST_ALIAS_REGEX = re.compile(r'^[a-zA-Z0-9_\-\.]+$')

"""
Проверка имени файла ключа:
- только буквы, цифры, дефисы, подчёркивания, точки
- не должно содержать слэшей
- не должно быть копий
"""
def is_valid_key_name(name: str) -> bool:
    if "/" in name or "\\" in name:
        return False
    if not KEY_NAME_REGEX.fullmatch(name):
        return False
    priv_path = SSH_DIR / name
    pub_path = SSH_DIR / f"{name}.pub"
    # проверка на существование
    return not priv_path.exists() and not pub_path.exists()


"""
Проверяет, допустим ли alias для Host в ~/.ssh/config
чтобы были латинские буквы, цифры, точки, дефисы, подчеркивание
"""
def is_valid_host_alias(alias: str) -> bool:
    if not HOST_ALIAS_REGEX.fullmatch(alias):
        return False

    # конфликты localhost, all, wildcard
    forbidden_hosts = {"*", "localhost", "default"}
    return alias.lower() not in forbidden_hosts


"""
Проверка пути:
- внутри домашней директории
- не выходит выше
- нет абсолютных и других путей
"""
def is_safe_file_path(path: str) -> bool:
    try:
        resolved = Path(path).expanduser().resolve() # приводим к абсолютному пути
        return str(resolved).startswith(str(Path.home())) # внутри домащней директории
    except Exception:
        return False
