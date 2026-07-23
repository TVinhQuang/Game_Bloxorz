from pathlib import Path

from bloxorz.core.game import BloxorzCoreGame
from bloxorz.solvers import (
    solve_astar,
    solve_bfs,
    solve_dfs,
    solve_ucs,
)


def source_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_level(level_number: int) -> BloxorzCoreGame:
    pattern = f"level_{level_number:02d}_*.json"
    matches = sorted((source_root() / "levels").glob(pattern))

    if len(matches) != 1:
        raise AssertionError(
            f"Expected one level matching {pattern}, found {len(matches)}"
        )

    return BloxorzCoreGame.from_level_file(matches[0])


def verify_solution(
    level_number: int,
    solution,
) -> None:
    """
    Chạy lại solution bằng game thật để chắc chắn đường đi hợp lệ.
    """

    replay_game = load_level(level_number)

    for action in solution:
        result = replay_game.move(action)

        assert result.valid, (
            f"Invalid action {action} in solver solution "
            f"for level {level_number}"
        )

    assert replay_game.is_goal_state(), (
        f"Solution did not reach the goal for level {level_number}"
    )


def test_all_solvers_on_level_1() -> None:
    solvers = [
        solve_bfs,
        solve_dfs,
        solve_ucs,
        solve_astar,
    ]

    for solver in solvers:
        game = load_level(1)
        result = solver(game)

        assert result.success, (
            f"{result.algorithm} failed on level 1"
        )

        verify_solution(1, result.solution)


def test_optimal_solver_lengths_match() -> None:
    """
    Khi Core dùng cost = 1:
    BFS, UCS và A* nên cho độ dài lời giải tối ưu giống nhau.
    """

    bfs_result = solve_bfs(load_level(1))
    ucs_result = solve_ucs(load_level(1))
    astar_result = solve_astar(load_level(1))

    assert bfs_result.solution_length == ucs_result.solution_length
    assert bfs_result.solution_length == astar_result.solution_length
    
def test_solver_starts_from_current_state() -> None:
    game = load_level(1)

    # Chọn một action hợp lệ từ Start.
    legal_actions = game.legal_actions()
    assert legal_actions

    manual_action = legal_actions[0]

    # Người chơi tự đi một bước.
    manual_result = game.move(manual_action)
    assert manual_result.valid

    current_state_before_search = game.state
    current_move_count = game.move_count

    # BFS phải tìm từ state hiện tại.
    solver_result = solve_bfs(game)

    assert solver_result.success

    # Solver không được tự sửa state thật của game.
    assert game.state == current_state_before_search
    assert game.move_count == current_move_count

    # Chạy lại solution từ đúng current state.
    for action in solver_result.solution:
        result = game.move(action)
        assert result.valid

    assert game.is_goal_state()


if __name__ == "__main__":
    test_all_solvers_on_level_1()
    test_optimal_solver_lengths_match()
    test_solver_starts_from_current_state()

    print("All solver tests passed.")