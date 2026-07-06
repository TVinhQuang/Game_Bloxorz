from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from bloxorz.core.enums import Direction
from bloxorz.core.game import BloxorzCoreGame


@dataclass(frozen=True)
class SolverResult:
    """
    Kết quả chuẩn mà mọi solver nên trả về.

    GUI và experiments sau này chỉ cần đọc object này,
    không cần biết bên trong BFS/DFS/UCS/A* code ra sao.
    """

    # Tên thuật toán, ví dụ: "BFS", "DFS", "UCS", "A*".
    algorithm: str

    # Solver có tìm được lời giải không.
    success: bool

    # Danh sách hành động tạo thành lời giải.
    solution: list[Direction]

    # Thời gian tìm kiếm, tính bằng giây.
    search_time: float

    # Bộ nhớ sử dụng, sau này có thể đo bằng tracemalloc.
    memory_usage: int

    # Số node đã expand.
    expanded_nodes: int

    # Độ dài solution, thường bằng len(solution).
    solution_length: int

    # Thông báo phụ để GUI hiển thị.
    message: str = ""


class SolverFunction(Protocol):
    """
    Protocol cho một hàm solver.

    Sau này BFS có thể là:
        def solve_bfs(game: BloxorzCoreGame) -> SolverResult:
            ...

    GUI chỉ cần gọi solver_func(game).
    """

    def __call__(self, game: BloxorzCoreGame) -> SolverResult:
        ...


def solver_not_implemented(algorithm: str) -> SolverResult:
    """
    Hàm stub tạm thời khi solver chưa được implement.

    GUI sẽ gọi hàm này khi người dùng bấm Solve BFS/DFS/UCS/A*
    trong giai đoạn ta chưa code solver.
    """

    return SolverResult(
        algorithm=algorithm,
        success=False,
        solution=[],
        search_time=0.0,
        memory_usage=0,
        expanded_nodes=0,
        solution_length=0,
        message=f"{algorithm} solver is not implemented yet.",
    )