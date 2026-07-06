from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LevelData:
    """
    Dữ liệu thô đọc từ file JSON.

    Core chỉ cần:
    - id
    - name
    - grid

    Nhưng ta vẫn giữ:
    - bridges
    - switches
    - split

    Lý do:
    Advanced tiles sau này có thể dùng lại đúng format này,
    không cần đổi level file.
    """

    id: int
    name: str
    difficulty: int
    category: str
    description: str
    grid: tuple[str, ...]

    legend: dict[str, str] = field(default_factory=dict)

    # Các field này để Advanced dùng sau.
    bridges: list[dict[str, Any]] = field(default_factory=list)
    switches: list[dict[str, Any]] = field(default_factory=list)
    split: dict[str, Any] | None = None


def load_level(level_path: str | Path) -> LevelData:
    """
    Đọc một level JSON và trả về LevelData.

    Hàm này chỉ parse dữ liệu.
    Việc kiểm tra board hợp lệ sẽ nằm trong Board.
    """

    path = Path(level_path)

    with path.open("r", encoding="utf-8") as file:
        raw = json.load(file)

    return LevelData(
        id=int(raw["id"]),
        name=str(raw["name"]),
        difficulty=int(raw.get("difficulty", 1)),
        category=str(raw.get("category", "core")),
        description=str(raw.get("description", "")),
        grid=tuple(raw["grid"]),
        legend=dict(raw.get("legend", {})),
        bridges=list(raw.get("bridges", [])),
        switches=list(raw.get("switches", [])),
        split=raw.get("split", None),
    )