from __future__ import annotations

import time
import tracemalloc

from bloxorz.core.game import BloxorzCoreGame
from bloxorz.core.state import BlockState
from bloxorz.solvers.base import SolverResult


def state_key(game: BloxorzCoreGame, state: BlockState) -> tuple:
    return game.encode_state(state).to_tuple()


def solve_dfs(game: BloxorzCoreGame) -> SolverResult:
    """
    Depth-First Search.

    DFS dùng stack LIFO và có reached set để tránh lặp vô hạn.
    DFS không đảm bảo tìm được lời giải ngắn nhất.
    """

    start_time = time.perf_counter()
    tracemalloc.start()

    expanded_nodes = 0
    # Bắt đầu tìm kiếm từ vị trí hiện tại của người chơi,
    # không bắt buộc quay về Start.
    initial_state = game.state

    # Stack chứa (state, path).
    stack = [(initial_state, [])]

    # DFS đánh dấu khi pop state ra để expand.
    reached: set[tuple] = set()

    success = False
    solution = []

    while stack:
        current_state, path = stack.pop()
        current_key = state_key(game, current_state)

        if current_key in reached:
            continue

        reached.add(current_key)
        expanded_nodes += 1

        if game.is_goal_state(current_state):
            success = True
            solution = path
            break

        successors = game.successors(current_state)

        # Stack là LIFO.
        # Dùng reversed để action xuất hiện trước trong DIRECTION_ORDER
        # được xét trước khi pop.
        for successor in reversed(successors):
            next_state = successor.state
            next_key = state_key(game, next_state)

            if next_key not in reached:
                stack.append(
                    (
                        next_state,
                        path + [successor.action],
                    )
                )

    search_time = time.perf_counter() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return SolverResult(
        algorithm="DFS",
        success=success,
        solution=solution,
        search_time=search_time,
        memory_usage=peak_memory,
        expanded_nodes=expanded_nodes,
        solution_length=len(solution),
        message=(
            "DFS found a solution."
            if success
            else "DFS could not find a solution."
        ),
    )