from enum import Enum


class Orientation(str, Enum):
    # Block đứng thẳng, chỉ chiếm đúng 1 ô.
    STANDING = "standing"

    # Block nằm ngang, chiếm 2 ô cạnh nhau theo chiều trái - phải.
    HORIZONTAL = "horizontal"

    # Block nằm dọc, chiếm 2 ô cạnh nhau theo chiều trên - dưới.
    VERTICAL = "vertical"


class Direction(str, Enum):
    # Lăn block lên trên.
    UP = "up"

    # Lăn block xuống dưới.
    DOWN = "down"

    # Lăn block sang trái.
    LEFT = "left"

    # Lăn block sang phải.
    RIGHT = "right"


class MoveStatus(str, Enum):
    # Move hợp lệ, block đã di chuyển.
    MOVED = "moved"

    # Move không hợp lệ, block giữ nguyên.
    INVALID = "invalid"

    # Move hợp lệ và sau move thì thắng.
    WON = "won"


# Thứ tự cố định rất quan trọng cho Solver sau này.
# Ví dụ BFS/DFS nếu duyệt action theo thứ tự này thì kết quả ổn định, dễ debug.
DIRECTION_ORDER = (
    Direction.UP,
    Direction.DOWN,
    Direction.LEFT,
    Direction.RIGHT,
)