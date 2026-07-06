from __future__ import annotations

from .level import LevelData, load_level


class Board:
    """
    Board Core của Bloxorz.

    Board chỉ chịu trách nhiệm:
    - lưu grid
    - kiểm tra biên
    - đọc ký hiệu ô
    - tìm start/goal
    - kiểm tra ô có phải void không

    Board không xử lý luật fragile/bridge/switch.
    Các luật đó sẽ đi qua RuleExtension trong rules.py.
    """

    VOID = "#"
    FLOOR = "."
    START = "S"
    GOAL = "G"

    def __init__(self, level_data: LevelData):
        self.level_data = level_data
        self.id = level_data.id
        self.name = level_data.name
        self.difficulty = level_data.difficulty
        self.category = level_data.category
        self.description = level_data.description
        self.grid = level_data.grid

        self.rows = len(self.grid)
        self.cols = len(self.grid[0]) if self.rows > 0 else 0

        self._validate_grid_shape()

        self.start = self._find_unique_cell(self.START)
        self.goal = self._find_unique_cell(self.GOAL)

    @classmethod
    def from_level_file(cls, level_path: str) -> "Board":
        # Đọc JSON thành LevelData.
        level_data = load_level(level_path)

        # Tạo Board từ LevelData.
        return cls(level_data)

    def _validate_grid_shape(self) -> None:
        # Board không được rỗng.
        if self.rows == 0:
            raise ValueError("Board grid must not be empty.")

        # Tất cả dòng phải có cùng số cột.
        for row in self.grid:
            if len(row) != self.cols:
                raise ValueError("All rows in grid must have the same length.")

    def _find_unique_cell(self, target: str) -> tuple[int, int]:
        # Lưu tất cả vị trí tìm được.
        positions: list[tuple[int, int]] = []

        # Duyệt toàn bộ board.
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == target:
                    positions.append((r, c))

        # Mỗi level phải có đúng 1 start hoặc 1 goal.
        if len(positions) != 1:
            raise ValueError(
                f"Expected exactly one '{target}' cell, found {len(positions)}."
            )

        return positions[0]

    def is_inside(self, r: int, c: int) -> bool:
        # Một tọa độ hợp lệ nếu nằm trong hình chữ nhật của board.
        return 0 <= r < self.rows and 0 <= c < self.cols

    def cell_at(self, r: int, c: int) -> str:
        # Nếu ra ngoài board thì xem như void.
        if not self.is_inside(r, c):
            return self.VOID

        return self.grid[r][c]

    def is_void_cell(self, r: int, c: int) -> bool:
        # Ô là void nếu ra ngoài board hoặc ký hiệu là '#'.
        return (not self.is_inside(r, c)) or self.cell_at(r, c) == self.VOID

    def is_base_support_cell(self, r: int, c: int) -> bool:
        """
        Kiểm tra ô có thể đỡ block theo luật Core hay không.

        Core chỉ có một loại không đỡ được: void '#'.

        Advanced sau này sẽ kiểm tra thêm:
        - fragile không được đứng lên
        - bridge đóng thì xem như void
        - split/cube rules
        """

        return not self.is_void_cell(r, c)

    def is_goal_cell(self, r: int, c: int) -> bool:
        # Goal được xác định bởi vị trí G trong level.
        return (r, c) == self.goal