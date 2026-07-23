from __future__ import annotations

import time
import tracemalloc
from collections import deque

from bloxorz.core.game import BloxorzCoreGame
from bloxorz.core.state import BlockState
from bloxorz.solvers.base import SolverResult


def state_key(game: BloxorzCoreGame, state: BlockState) -> tuple:
    """
    Chuyển state thành key hashable cho visited.

    Core hiện trả:
        (r, c, orientation)

    Sau này nếu Advanced bổ sung bridge state,
    encode_state() có thể đưa thêm dữ liệu vào key.
    """

    return game.encode_state(state).to_tuple()


def solve_bfs(game: BloxorzCoreGame) -> SolverResult:
    """
    Breadth-First Search.

    BFS mở rộng các node theo độ sâu tăng dần.
    Khi mọi move có cost bằng nhau, BFS tìm được lời giải ngắn nhất
    theo số lượng move.
    """

    start_time = time.perf_counter()
    tracemalloc.start()

    expanded_nodes = 0

    # Bắt đầu tìm kiếm từ vị trí hiện tại của người chơi,
    # không bắt buộc quay về Start.
    initial_state = game.state

    # Mỗi phần tử gồm:
    # (state hiện tại, đường đi tới state đó)
    frontier = deque([(initial_state, [])])

    # Đánh dấu reached ngay khi đưa state vào frontier.
    reached = {state_key(game, initial_state)}

    success = False
    solution = []

    while frontier:
        current_state, path = frontier.popleft()
        expanded_nodes += 1

        # Goal test.
        if game.is_goal_state(current_state):
            success = True
            solution = path
            break

        # Sinh successor bằng chính Core engine.
        for successor in game.successors(current_state):
            next_state = successor.state
            action = successor.action
            next_key = state_key(game, next_state)

            if next_key in reached:
                continue

            reached.add(next_key)
            frontier.append((next_state, path + [action]))

    search_time = time.perf_counter() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return SolverResult(
        algorithm="BFS",
        success=success,
        solution=solution,
        search_time=search_time,
        memory_usage=peak_memory,
        expanded_nodes=expanded_nodes,
        solution_length=len(solution),
        message=(
            "BFS found a solution."
            if success
            else "BFS could not find a solution."
        ),
    )