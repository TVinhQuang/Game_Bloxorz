from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable

from .enums import Orientation


@dataclass(frozen=True)
class BlockState:
    """
    Trạng thái hình học của block 1 x 1 x 2.

    Quy ước:
    - r là row của ô neo.
    - c là column của ô neo.
    - orientation cho biết block đứng, nằm ngang, hay nằm dọc.

    Với block nằm ngang:
        anchor = (r, c)
        occupied cells = (r, c), (r, c + 1)

    Với block nằm dọc:
        anchor = (r, c)
        occupied cells = (r, c), (r + 1, c)
    """

    r: int
    c: int
    orientation: Orientation

    def occupied_cells(self) -> tuple[tuple[int, int], ...]:
        # Nếu block đứng, nó chỉ chiếm 1 ô.
        if self.orientation == Orientation.STANDING:
            return ((self.r, self.c),)

        # Nếu block nằm ngang, nó chiếm 2 ô cùng dòng.
        if self.orientation == Orientation.HORIZONTAL:
            return ((self.r, self.c), (self.r, self.c + 1))

        # Nếu block nằm dọc, nó chiếm 2 ô cùng cột.
        if self.orientation == Orientation.VERTICAL:
            return ((self.r, self.c), (self.r + 1, self.c))

        raise ValueError(f"Unknown orientation: {self.orientation}")

    def to_key(self) -> tuple[int, int, str]:
        """
        Trả về key hashable cho solver.

        BFS/DFS/UCS/A* cần lưu visited/reached set.
        Vì vậy state phải chuyển thành tuple ổn định, hash được.
        """

        return (self.r, self.c, self.orientation.value)


@dataclass(frozen=True)
class GameStateKey:
    """
    Key đầy đủ của một game state để solver dùng.

    Core hiện tại chỉ có block.
    Nhưng sau này Advanced cần thêm:
    - bridge open/closed states
    - split mode
    - active cube
    - cube positions

    Vì vậy ta để extra là tuple Hashable.
    Core dùng extra = ().
    Advanced sẽ override thông qua RuleExtension.
    """

    block_key: tuple[int, int, str]
    extra: tuple[Hashable, ...] = ()

    def to_tuple(self) -> tuple[Hashable, ...]:
        # Gom block_key và extra thành một tuple duy nhất.
        return (*self.block_key, *self.extra)