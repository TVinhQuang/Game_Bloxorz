from __future__ import annotations

import heapq
import math
import time
import tracemalloc

from bloxorz.core.game import BloxorzCoreGame
from bloxorz.core.state import BlockState
from bloxorz.solvers.base import SolverResult


def state_key(game: BloxorzCoreGame, state: BlockState) -> tuple:
    return game.encode_state(state).to_tuple()


def calculate_heuristic(
    state: BlockState,
    goal_position: tuple[int, int],
) -> int:
    """
    Heuristic cho Core Bloxorz.

    Ta lấy Manhattan distance lớn nhất từ các ô block đang chiếm
    đến goal rồi chia 2 và làm tròn lên.

    Lý do chia 2:
    Một lần lăn có thể làm một phần block dịch tối đa 2 ô theo
    Manhattan distance.

    Không cộng orientation penalty riêng để tránh double-counting.
    """

    goal_r, goal_c = goal_position

    distances = [
        abs(r - goal_r) + abs(c - goal_c)
        for r, c in state.occupied_cells()
    ]

    return math.ceil(max(distances) / 2)


def solve_astar(game: BloxorzCoreGame) -> SolverResult:
    """
    A* Search sử dụng:
        f(n) = g(n) + h(n)
    """

    start_time = time.perf_counter()
    tracemalloc.start()

    expanded_nodes = 0
    counter = 0

    # Bắt đầu tìm kiếm từ vị trí hiện tại của người chơi,
    # không bắt buộc quay về Start.
    initial_state = game.state
    goal_position = game.board.goal

    initial_h = calculate_heuristic(
        initial_state,
        goal_position,
    )

    # Heap item:
    # (f, h, counter, g, state, path)
    frontier = [
        (
            initial_h,
            initial_h,
            counter,
            0.0,
            initial_state,
            [],
        )
    ]

    g_scores = {
        state_key(game, initial_state): 0.0
    }

    success = False
    solution = []

    while frontier:
        (
            _f,
            _h,
            _,
            g_cost,
            current_state,
            path,
        ) = heapq.heappop(frontier)

        current_key = state_key(game, current_state)

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

            new_g = g_cost + successor.cost

            if new_g >= g_scores.get(next_key, float("inf")):
                continue

            g_scores[next_key] = new_g

            new_h = calculate_heuristic(
                next_state,
                goal_position,
            )

            new_f = new_g + new_h
            counter += 1

            heapq.heappush(
                frontier,
                (
                    new_f,
                    new_h,
                    counter,
                    new_g,
                    next_state,
                    path + [successor.action],
                ),
            )

    search_time = time.perf_counter() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return SolverResult(
        algorithm="A*",
        success=success,
        solution=solution,
        search_time=search_time,
        memory_usage=peak_memory,
        expanded_nodes=expanded_nodes,
        solution_length=len(solution),
        message=(
            "A* found a solution."
            if success
            else "A* could not find a solution."
        ),
    )