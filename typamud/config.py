from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
VAR_DIR = BASE_DIR / "var"
DB_PATH = VAR_DIR / "typamud.db"
WORLD_PATH = DATA_DIR / "world.json"


@dataclass(slots=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 4000
    tick_interval: float = 2.0
    db_path: Path = DB_PATH
    world_path: Path = WORLD_PATH
    motd: str = "Добро пожаловать в typamud. Введите имя персонажа:"


settings = Settings()
