from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / ".cat_pet"
CONFIG_PATH = CONFIG_DIR / "config.json"


@dataclass(slots=True)
class PetConfig:
    pet_size: int = 280
    window_x: int | None = None
    window_y: int | None = None
    active_asset_path: str | None = None
    active_asset_name: str | None = None
    asset_status: str = "empty"
    processed_frames_dir: str | None = None
    frame_interval_ms: int = 66


def load_config() -> PetConfig:
    if not CONFIG_PATH.exists():
        return PetConfig()

    try:
        data: dict[str, Any] = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return PetConfig()

    allowed = {field.name for field in PetConfig.__dataclass_fields__.values()}
    filtered = {key: value for key, value in data.items() if key in allowed}
    return PetConfig(**filtered)


def save_config(config: PetConfig) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(asdict(config), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
