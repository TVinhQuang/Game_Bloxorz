from pathlib import Path

from bloxorz.core.board import Board
from bloxorz.core.enums import Direction, Orientation
from bloxorz.core.game import BloxorzCoreGame
from bloxorz.core.level import load_level
from bloxorz.core.movement import compute_next_state
from bloxorz.core.state import BlockState


def project_root() -> Path:
    # tests/test_core_mechanics.py nằm trong Source/tests.
    # parents[1] chính là Source/.
    return Path(__file__).resolve().parents[1]


def test_level_loader() -> None:
    level_path = project_root() / "levels" / "level_01_core_intro.json"

    level = load_level(level_path)

    assert level.id == 1
    assert level.name == "Core Platform"
    assert sum(row.count("S") for row in level.grid) == 1
    assert sum(row.count("G") for row in level.grid) == 1


def test_board_start_goal() -> None:
    level_path = project_root() / "levels" / "level_01_core_intro.json"

    board = Board.from_level_file(str(level_path))

    assert board.start == (1, 1)
    assert board.goal == (1, 4)
    assert board.is_goal_cell(1, 4)
    assert not board.is_goal_cell(1, 1)


def test_occupied_cells() -> None:
    standing = BlockState(2, 3, Orientation.STANDING)
    assert standing.occupied_cells() == ((2, 3),)

    horizontal = BlockState(2, 3, Orientation.HORIZONTAL)
    assert horizontal.occupied_cells() == ((2, 3), (2, 4))

    vertical = BlockState(2, 3, Orientation.VERTICAL)
    assert vertical.occupied_cells() == ((2, 3), (3, 3))


def test_transition_from_standing() -> None:
    state = BlockState(3, 3, Orientation.STANDING)

    assert compute_next_state(state, Direction.UP) == BlockState(
        1,
        3,
        Orientation.VERTICAL,
    )

    assert compute_next_state(state, Direction.DOWN) == BlockState(
        4,
        3,
        Orientation.VERTICAL,
    )

    assert compute_next_state(state, Direction.LEFT) == BlockState(
        3,
        1,
        Orientation.HORIZONTAL,
    )

    assert compute_next_state(state, Direction.RIGHT) == BlockState(
        3,
        4,
        Orientation.HORIZONTAL,
    )


def test_transition_from_horizontal() -> None:
    state = BlockState(3, 3, Orientation.HORIZONTAL)

    assert compute_next_state(state, Direction.UP) == BlockState(
        2,
        3,
        Orientation.HORIZONTAL,
    )

    assert compute_next_state(state, Direction.DOWN) == BlockState(
        4,
        3,
        Orientation.HORIZONTAL,
    )

    assert compute_next_state(state, Direction.LEFT) == BlockState(
        3,
        2,
        Orientation.STANDING,
    )

    assert compute_next_state(state, Direction.RIGHT) == BlockState(
        3,
        5,
        Orientation.STANDING,
    )


def test_transition_from_vertical() -> None:
    state = BlockState(3, 3, Orientation.VERTICAL)

    assert compute_next_state(state, Direction.UP) == BlockState(
        2,
        3,
        Orientation.STANDING,
    )

    assert compute_next_state(state, Direction.DOWN) == BlockState(
        5,
        3,
        Orientation.STANDING,
    )

    assert compute_next_state(state, Direction.LEFT) == BlockState(
        3,
        2,
        Orientation.VERTICAL,
    )

    assert compute_next_state(state, Direction.RIGHT) == BlockState(
        3,
        4,
        Orientation.VERTICAL,
    )


def test_level_01_solution() -> None:
    level_path = project_root() / "levels" / "level_01_core_intro.json"

    game = BloxorzCoreGame.from_level_file(level_path)

    assert not game.is_goal_state()

    result_1 = game.move(Direction.RIGHT)
    assert result_1.valid
    assert not result_1.won
    assert game.state.orientation == Orientation.HORIZONTAL

    result_2 = game.move(Direction.RIGHT)
    assert result_2.valid
    assert result_2.won
    assert game.state.orientation == Orientation.STANDING
    assert game.state.r == game.board.goal[0]
    assert game.state.c == game.board.goal[1]


def test_invalid_move_into_void() -> None:
    level_path = project_root() / "levels" / "level_01_core_intro.json"

    game = BloxorzCoreGame.from_level_file(level_path)

    result = game.move(Direction.UP)

    assert not result.valid
    assert result.old_state == result.new_state
    assert game.state == game.initial_state


def test_successors_from_initial_state() -> None:
    level_path = project_root() / "levels" / "level_01_core_intro.json"

    game = BloxorzCoreGame.from_level_file(level_path)

    successors = game.successors()

    actions = {successor.action for successor in successors}

    assert Direction.RIGHT in actions
    assert Direction.UP not in actions
    assert Direction.DOWN not in actions
    assert Direction.LEFT not in actions


def main() -> None:
    test_level_loader()
    test_board_start_goal()
    test_occupied_cells()
    test_transition_from_standing()
    test_transition_from_horizontal()
    test_transition_from_vertical()
    test_level_01_solution()
    test_invalid_move_into_void()
    test_successors_from_initial_state()

    print("All core mechanics tests passed.")


if __name__ == "__main__":
    main()