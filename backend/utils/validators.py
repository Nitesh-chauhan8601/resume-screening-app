import re
from typing import Iterable


def allowed_file(filename: str, allowed_extensions: set[str]) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def split_multi_value(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        values = value
    else:
        values = re.split(r"[,|\n/]+", str(value))
    cleaned = [item.strip() for item in values if item and item.strip()]
    return list(dict.fromkeys(cleaned))


def join_multi_value(values: Iterable[str]) -> str:
    return ", ".join(split_multi_value(list(values)))


def as_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def as_bool(value) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}
