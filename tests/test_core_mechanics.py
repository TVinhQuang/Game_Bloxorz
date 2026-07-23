from pathlib import Path

from bloxorz.core.board import Board
from bloxorz.core.enums import Direction, Orientation
from bloxorz.core.game import BloxorzCoreGame
from bloxorz.core.level import load_level
from bloxorz.core.movement import compute_next_state
from bloxorz.core.state import BlockState

from pathlib import Path

from bloxorz.core.board import Board
from bloxorz.core.enums import Direction, Orientation
from bloxorz.core.game import BloxorzCoreGame
from bloxorz.core.level import LevelData, load_level
from bloxorz.core.movement import compute_next_state
from bloxorz.core.state import BlockState


def project_root() -> Path:
    # tests/test_core_mechanics.py nằm trong Source/tests.
    # parents[1] chính là Source/.
    return Path(__file__).resolve().parents[1]

def create_tiny_core_game() -> BloxorzCoreGame:
    """
    Tạo level Core cực nhỏ chỉ dùng cho unit test.

    Layout:

        ######
        #S..G#
        ######

    Lời giải chắc chắn:
        RIGHT, RIGHT

    Không dùng level thật trong thư mục levels/,
    vì các level thật có thể tiếp tục được chỉnh sửa.
    """

    level_data = LevelData(
        id=999,
        name="Tiny Core Test",
        difficulty=1,
        category="test",
        description="Deterministic level used only for Core unit tests.",
        grid=(
            "######",
            "#S..G#",
            "######",
        ),
        legend={
            "#": "void",
            ".": "floor",
            "S": "start",
            "G": "goal",
        },
        bridges=[],
        switches=[],
        split=None,
    )

    board = Board(level_data)

    return BloxorzCoreGame(board)


def test_board_start_goal() -> None:
    game = create_tiny_core_game()
    board = game.board

    assert board.start == (1, 1)
    assert board.goal == (1, 4)

    assert board.cell_at(1, 1) == Board.START
    assert board.cell_at(1, 4) == Board.GOAL

    assert board.is_goal_cell(1, 4)
    assert not board.is_goal_cell(1, 1)


def test_board_start_goal() -> None:
    level_path = (
        project_root()
        / "levels"
        / "level_01_core_intro.json"
    )

    board = Board.from_level_file(
        str(level_path)
    )

    start_r, start_c = board.start
    goal_r, goal_c = board.goal

    # Start và Goal phải nằm trong board.
    assert board.is_inside(start_r, start_c)
    assert board.is_inside(goal_r, goal_c)

    # Các tọa độ tìm được phải đúng ký hiệu trong grid.
    assert board.cell_at(start_r, start_c) == Board.START
    assert board.cell_at(goal_r, goal_c) == Board.GOAL

    # Goal test phải nhận đúng goal.
    assert board.is_goal_cell(goal_r, goal_c)

    # Start không được đồng thời là goal.
    assert not board.is_goal_cell(start_r, start_c)

    # Start và Goal phải khác nhau.
    assert board.start != board.goal


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


def test_two_move_core_solution() -> None:
    """
    Kiểm tra một lời giải Core đơn giản và xác định trước.
    """

    game = create_tiny_core_game()

    assert not game.is_goal_state()
    assert game.move_count == 0

    # Move RIGHT lần 1:
    # block từ standing chuyển sang horizontal.
    result_1 = game.move(Direction.RIGHT)

    assert result_1.valid
    assert not result_1.won
    assert game.state.orientation == Orientation.HORIZONTAL
    assert game.move_count == 1

    # Move RIGHT lần 2:
    # block từ horizontal chuyển thành standing trên goal.
    result_2 = game.move(Direction.RIGHT)

    assert result_2.valid
    assert result_2.won
    assert game.is_goal_state()
    assert game.state.orientation == Orientation.STANDING
    assert game.state == BlockState(
        1,
        4,
        Orientation.STANDING,
    )
    assert game.move_count == 2

def test_invalid_move_into_void() -> None:
    game = create_tiny_core_game()

    initial_state = game.state

    # Từ Start, lăn UP sẽ đi vào void.
    result = game.move(Direction.UP)

    assert not result.valid

    # Invalid move không làm state thay đổi.
    assert game.state == initial_state

    # Invalid move không được tính vào move counter.
    assert game.move_count == 0

    assert not game.is_goal_state()


def test_successors_from_initial_state() -> None:
    game = create_tiny_core_game()

    successors = game.successors()

    actions = {
        successor.action
        for successor in successors
    }

    # Chỉ RIGHT hợp lệ trên tiny level.
    assert actions == {
        Direction.RIGHT,
    }

    right_successor = successors[0]

    assert right_successor.action == Direction.RIGHT
    assert right_successor.state == BlockState(
        1,
        2,
        Orientation.HORIZONTAL,
    )
    assert right_successor.cost == 1.0

def test_level_loader() -> None:
    level_path = (
        project_root()
        / "levels"
        / "level_01_core_intro.json"
    )

    level = load_level(level_path)

    assert level.id == 1
    assert level.name.strip() != ""
    assert level.difficulty == 1

    # Level 1 hiện tại là Advanced.
    assert level.category == "advanced"

    # Grid phải tồn tại và là hình chữ nhật.
    assert len(level.grid) > 0

    row_lengths = {
        len(row)
        for row in level.grid
    }

    assert len(row_lengths) == 1

    # Có đúng một Start và một Goal.
    start_count = sum(
        row.count("S")
        for row in level.grid
    )

    goal_count = sum(
        row.count("G")
        for row in level.grid
    )

    assert start_count == 1
    assert goal_count == 1
    
LEVEL_FILES = [
    "level_01_core_intro.json",
    "level_02_core_turning.json",
    "level_03_core_voids.json",
    "level_04_core_maze.json",
    "level_05_core_broken_causeway.json",
    "level_06_core_spiral_descent.json",
    "level_07_core_island_maze.json",
    "level_08_core_deep_zigzag.json",
    "level_09_core_dense_labyrinth.json",
    "level_10_core_final_challenge.json",
]

def test_all_official_levels_are_well_formed() -> None:
    """
    Kiểm tra cấu trúc chung của 10 level chính thức.

    Không kiểm tra tọa độ cụ thể vì level có thể được thiết kế lại.
    """

    for expected_id, filename in enumerate(
        LEVEL_FILES,
        start=1,
    ):
        level_path = (
            project_root()
            / "levels"
            / filename
        )

        level = load_level(level_path)

        # ID và difficulty tăng từ 1 đến 10.
        assert level.id == expected_id
        assert level.difficulty == expected_id

        # Metadata cơ bản.
        assert level.name.strip() != ""
        assert level.description.strip() != ""

        # Grid không rỗng và phải hình chữ nhật.
        assert len(level.grid) > 0

        row_lengths = {
            len(row)
            for row in level.grid
        }

        assert len(row_lengths) == 1, (
            f"{filename} has non-rectangular rows: "
            f"{row_lengths}"
        )

        # Có đúng một Start và một Goal.
        start_count = sum(
            row.count("S")
            for row in level.grid
        )

        goal_count = sum(
            row.count("G")
            for row in level.grid
        )

        assert start_count == 1, (
            f"{filename} must have exactly one S"
        )

        assert goal_count == 1, (
            f"{filename} must have exactly one G"
        )

        # Kiểm tra ký hiệu hợp lệ.
        symbols = set(
            "".join(level.grid)
        )

        if level.category == "core":
            allowed_symbols = {
                "#",
                ".",
                "S",
                "G",
            }

        elif level.category == "advanced":
            allowed_symbols = {
                "#",
                ".",
                "S",
                "G",
                "F",
                "B",
                "X",
                "O",
                "P",
            }

        else:
            raise AssertionError(
                f"Unknown category in {filename}: "
                f"{level.category}"
            )

        unexpected_symbols = (
            symbols - allowed_symbols
        )

        assert not unexpected_symbols, (
            f"{filename} contains invalid symbols: "
            f"{unexpected_symbols}"
        )
        
def test_level_01_advanced_solution() -> None:
    level_path = (
        project_root()
        / "levels"
        / "level_01_core_intro.json"
    )

    game = BloxorzCoreGame.from_level_file(
        level_path,
        rule_extension=AdvancedRuleExtension(
            level_path
        ),
    )

    solution = [
        Direction.DOWN,
        Direction.RIGHT,
        Direction.UP,
        Direction.RIGHT,
        Direction.DOWN,
        Direction.DOWN,
        Direction.RIGHT,
        Direction.RIGHT,
        Direction.DOWN,
        Direction.DOWN,
        Direction.RIGHT,
    ]

    for move_number, action in enumerate(
        solution,
        start=1,
    ):
        result = game.move(action)

        assert result.valid, (
            f"Move {move_number} "
            f"({action.value}) is invalid"
        )

    assert game.is_goal_state()
    assert game.move_count == 11

def main() -> None:
    test_level_loader()
    test_board_start_goal()
    test_occupied_cells()
    test_transition_from_standing()
    test_transition_from_horizontal()
    test_transition_from_vertical()

    # Tên mới.
    test_two_move_core_solution()

    test_invalid_move_into_void()
    test_successors_from_initial_state()
    test_all_official_levels_are_well_formed()

    print("All core mechanics tests passed.")


if __name__ == "__main__":
    main()