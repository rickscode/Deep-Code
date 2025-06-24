import chardet
from pathlib import Path
from typing import Optional
import shutil
import os

class FileOperationError(Exception):
    pass

def read_file_safe(filepath: str) -> str:
    path = Path(filepath)
    if not path.exists():
        raise FileOperationError(f"File not found: {filepath}")
    with open(filepath, 'rb') as f:
        raw = f.read()
        encoding = chardet.detect(raw)["encoding"] or "utf-8"
    return raw.decode(encoding)

def write_file_atomic(filepath: str, content: str, backup: bool = True):
    path = Path(filepath)
    if backup and path.exists():
        backup_path = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(str(path), str(backup_path))
    tmp_path = str(path) + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp_path, str(path))
