from pathlib import Path
from uuid import uuid4
import shutil
from fastapi import UploadFile
from app.core.config import settings

BASE_DIR = Path(__file__).resolve().parents[2]


def get_storage_root() -> Path:
    storage_path = Path(settings.FILE_STORAGE_PATH)
    if not storage_path.is_absolute():
        storage_path = BASE_DIR / storage_path
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


def save_upload_file(upload_file: UploadFile) -> tuple[str, int, str]:
    storage_dir = get_storage_root()
    safe_name = upload_file.filename.replace(' ', '_')
    filename = f"{uuid4().hex}_{safe_name}"
    file_path = storage_dir / filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    file_size = file_path.stat().st_size
    content_type = upload_file.content_type or "application/octet-stream"
    return filename, file_size, content_type


def resolve_file_path(stored_path: str) -> Path:
    path = Path(stored_path)
    if path.is_absolute():
        return path
    storage_dir = get_storage_root()
    return storage_dir / path
