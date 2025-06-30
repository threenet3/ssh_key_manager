import shutil
from pathlib import Path
import os

"""
Создаёт ~/.ssh, если не существует и устанавливает права
"""
def ensure_ssh_dir_exists() -> None:
    ssh_path = Path.home() / ".ssh"
    ssh_path.mkdir(mode=0o700, exist_ok=True)
    os.chmod(ssh_path, 0o700)


"""
проверка, существует ли файл по указанному пути

"""
def file_exists(path: Path) -> bool:
    return path.exists() and path.is_file()


"""
копирование файла (из src в dst) с возможностью перезаписи
если overwrite=True то перезапись, False - и файл есть, тогда ничего
"""
def copy_file(src: Path, dst: Path, overwrite: bool = False) -> bool:
    if dst.exists() and not overwrite: # если не указано, не перезаписываем
        return False
    try:
        shutil.copy2(src, dst) # копируем с сохранением метаданных
        return True
    except Exception as e:
        print(f"[ERROR] copy_file: {e}")
        return False


"""
удаление файла

"""
def delete_file(path: Path) -> bool:
    try:
        if path.exists():
            path.unlink()
        return True
    except Exception as e:
        print(f"[ERROR] delete_file: {e}")
        return False



"""
чтение файла
содержимое как строка, если ошибка - пустая строка
"""
def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"[ERROR] read_file: {e}")
        return ""



"""
запись в файл
"""
def write_file(path: Path, content: str) -> bool:
    try:
        path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"[ERROR] write_file: {e}")
        return False
