import os
import subprocess
from pathlib import Path
from typing import List, Optional

# путь к директрии
SSH_DIR = Path.home() / ".ssh"


"""
Возвращает список приватных ключей в ~/.ssh

ключ будет считаться приватным, если
- является обычным файлом
- не имеет расширение файла .pub
- имеет права доступа (только для владельца)
"""
def is_private_key_file(path: Path) -> bool:
    try:
        content = path.read_text(errors='ignore')
        return "-----BEGIN OPENSSH PRIVATE KEY-----" in content
    except Exception:
        return False

def list_keys() -> list[str]:
    ssh_dir = SSH_DIR
    return [
        f.name for f in ssh_dir.iterdir()
        if f.is_file() and is_private_key_file(f)
    ]

"""
Проверяет, является ли файл приватным SSH ключом (не .pub и без расширения + права доступа)
"""
def is_private_key(file_path: Path) -> bool:
    return file_path.is_file() and not file_path.name.endswith(".pub") and file_path.stat().st_mode & 0o077 == 0


"""
Генерация новой пары ключей с указанным именем и типом

key_name: имя файла ключа без расширения
key_type: тип ключа
passphrase: пароль (опционально при создании)
comment: комментарий
return: True, если успешно и наоборот False
"""
def generate_keypair(key_name: str,
                     key_type: str = "ed25519",
                     passphrase: Optional[str] = None,
                     comment: str = "") -> bool:
    key_path = SSH_DIR / key_name
    args = [
        "ssh-keygen",
        "-t", key_type,
        "-f", str(key_path),
        "-C", comment,
        "-N", passphrase if passphrase is not None else ""
    ]

    # создаем ~/.ssh с правами 700, если еще нету
    SSH_DIR.mkdir(mode=0o700, exist_ok=True)

    try:
        result = subprocess.run(args, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] generate_keypair: {e}")
        return False

"""
Удаляет приватный и публичный ключ по имени

key_name: имя ключа
return: если оба ключа удалены - True, иначе - False
"""
def delete_keypair(key_name: str) -> bool:
    priv_path = SSH_DIR / key_name
    pub_path = SSH_DIR / f"{key_name}.pub"
    success = True

    for path in [priv_path, pub_path]:
        try:
            if path.exists():
                path.unlink()
        except Exception as e:
            print(f"[ERROR] delete_keypair: {e}")
            success = False

    return success

"""
Возвращает содержимое публичного ключа
"""
def get_public_key(key_name: str) -> Optional[str]:
    pub_path = SSH_DIR / f"{key_name}.pub"
    if pub_path.exists():
        return pub_path.read_text().strip()
    return None


"""
Проверка на существующую пару (приватный и публичный ключи)

возвращает True если оба файла существуют
"""
def key_exists(key_name: str) -> bool:
    priv = SSH_DIR / key_name
    pub = SSH_DIR / f"{key_name}.pub"
    return priv.exists() and pub.exists()
