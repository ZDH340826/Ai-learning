from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .config import PROJECT_ROOT


INPUT_DIR = PROJECT_ROOT / "assets" / "input"
PROCESSED_DIR = PROJECT_ROOT / "assets" / "processed"

SUPPORTED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".mkv",
    ".avi",
    ".webm",
    ".gif",
}


@dataclass(frozen=True, slots=True)
class ImportedAsset:
    source_path: Path
    stored_path: Path
    display_name: str


def ensure_asset_dirs() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def is_supported_video(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_VIDEO_EXTENSIONS


def import_video(source_path: Path) -> ImportedAsset:
    source_path = source_path.expanduser().resolve()
    if not source_path.exists() or not source_path.is_file():
        raise FileNotFoundError(f"Video file does not exist: {source_path}")
    if not is_supported_video(source_path):
        raise ValueError(f"Unsupported video format: {source_path.suffix}")

    ensure_asset_dirs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_stem = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in source_path.stem)
    stored_name = f"{timestamp}_{safe_stem}{source_path.suffix.lower()}"
    stored_path = INPUT_DIR / stored_name
    shutil.copy2(source_path, stored_path)

    return ImportedAsset(
        source_path=source_path,
        stored_path=stored_path,
        display_name=source_path.name,
    )

