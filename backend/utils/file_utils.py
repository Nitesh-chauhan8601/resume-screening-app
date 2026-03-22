from datetime import datetime
from pathlib import Path
from uuid import uuid4

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


def ensure_folder(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def save_uploaded_file(file_storage: FileStorage, upload_folder: str) -> tuple[str, str]:
    ensure_folder(upload_folder)
    original_name = secure_filename(file_storage.filename or "resume")
    extension = Path(original_name).suffix.lower()
    unique_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid4().hex}{extension}"
    saved_path = Path(upload_folder) / unique_name
    file_storage.save(saved_path)
    return original_name, str(saved_path)
