from __future__ import annotations

from .enums import Direction, Orientation
from .state import BlockState


def compute_next_state(state: BlockState, direction: Direction) -> BlockState:
    """
    Tính state tiếp theo theo luật hình học của Bloxorz.

    Hàm này chỉ tính orientation transition.
    Nó chưa kiểm tra:
    - có rơi ra ngoài board không
    - có đè lên void không
    - có đứng trên fragile không
    - có bridge đóng không
    """

    r = state.r
    c = state.c
    orientation = state.orientation

    if orientation == Orientation.STANDING:
        if direction == Direction.UP:
            # Đứng tại (r, c), lăn lên chiếm (r - 2, c), (r - 1, c).
            return BlockState(r - 2, c, Orientation.VERTICAL)

        if direction == Direction.DOWN:
            # Đứng tại (r, c), lăn xuống chiếm (r + 1, c), (r + 2, c).
            return BlockState(r + 1, c, Orientation.VERTICAL)

        if direction == Direction.LEFT:
            # Đứng tại (r, c), lăn trái chiếm (r, c - 2), (r, c - 1).
            return BlockState(r, c - 2, Orientation.HORIZONTAL)

        if direction == Direction.RIGHT:
            # Đứng tại (r, c), lăn phải chiếm (r, c + 1), (r, c + 2).
            return BlockState(r, c + 1, Orientation.HORIZONTAL)

    if orientation == Orientation.HORIZONTAL:
        if direction == Direction.UP:
            # Nằm ngang, lăn lên thì vẫn nằm ngang, dịch lên 1 dòng.
            return BlockState(r - 1, c, Orientation.HORIZONTAL)

        if direction == Direction.DOWN:
            # Nằm ngang, lăn xuống thì vẫn nằm ngang, dịch xuống 1 dòng.
            return BlockState(r + 1, c, Orientation.HORIZONTAL)

        if direction == Direction.LEFT:
            # Nằm ngang tại (r,c),(r,c+1), lăn trái thì đứng tại (r,c-1).
            return BlockState(r, c - 1, Orientation.STANDING)

        if direction == Direction.RIGHT:
            # Nằm ngang tại (r,c),(r,c+1), lăn phải thì đứng tại (r,c+2).
            return BlockState(r, c + 2, Orientation.STANDING)

    if orientation == Orientation.VERTICAL:
        if direction == Direction.UP:
            # Nằm dọc tại (r,c),(r+1,c), lăn lên thì đứng tại (r-1,c).
            return BlockState(r - 1, c, Orientation.STANDING)

        if direction == Direction.DOWN:
            # Nằm dọc tại (r,c),(r+1,c), lăn xuống thì đứng tại (r+2,c).
            return BlockState(r + 2, c, Orientation.STANDING)

        if direction == Direction.LEFT:
            # Nằm dọc, lăn trái thì vẫn nằm dọc, dịch trái 1 cột.
            return BlockState(r, c - 1, Orientation.VERTICAL)

        if direction == Direction.RIGHT:
            # Nằm dọc, lăn phải thì vẫn nằm dọc, dịch phải 1 cột.
            return BlockState(r, c + 1, Orientation.VERTICAL)

    raise ValueError(f"Unsupported state or direction: {state}, {direction}")