from __future__ import annotations

import heapq
import time
import tracemalloc

from bloxorz.core.game import BloxorzCoreGame
from bloxorz.core.state import BlockState
from bloxorz.solvers.base import SolverResult


def state_key(game: BloxorzCoreGame, state: BlockState) -> tuple:
    return game.encode_state(state).to_tuple()


def solve_ucs(game: BloxorzCoreGame) -> SolverResult:
    """
    Uniform-Cost Search.

    UCS luôn expand state có tổng path cost g(n) nhỏ nhất.
    """

    start_time = time.perf_counter()
    tracemalloc.start()

    expanded_nodes = 0
    counter = 0

    # Bắt đầu tìm kiếm từ vị trí hiện tại của người chơi,
    # không bắt buộc quay về Start.
    initial_state = game.state
    initial_key = state_key(game, initial_state)

    # Heap item:
    # (g_cost, counter, state, path)
    frontier = [
        (
            0.0,
            counter,
            initial_state,
            [],
        )
    ]

    # Chi phí tốt nhất đã biết tới mỗi state.
    g_scores = {initial_key: 0.0}

    success = False
    solution = []

    while frontier:
        g_cost, _, current_state, path = heapq.heappop(frontier)
        current_key = state_key(game, current_state)

        # Bỏ qua entry cũ nếu đã có đường tốt hơn tới state này.
        if g_cost > g_scores.get(current_key, float("inf")):
            continue

        expanded_nodes += 1

        if game.is_goal_state(current_state):
            success = True
            solution = path
            break

        for successor in game.successors(current_state):
            next_state = successor.state
            next_key = state_key(game, next_state)

            # Lấy cost từ Core/RuleExtension.
            step_cost = successor.cost
            new_g = g_cost + step_cost

            if new_g >= g_scores.get(next_key, float("inf")):
                continue

            g_scores[next_key] = new_g
            counter += 1

            heapq.heappush(
                frontier,
                (
                    new_g,
                    counter,
                    next_state,
                    path + [successor.action],
                ),
            )

    search_time = time.perf_counter() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return SolverResult(
        algorithm="UCS",
        success=success,
        solution=solution,
        search_time=search_time,
        memory_usage=peak_memory,
        expanded_nodes=expanded_nodes,
        solution_length=len(solution),
        message=(
            "UCS found a solution."
            if success
            else "UCS could not find a solution."
        ),
    )