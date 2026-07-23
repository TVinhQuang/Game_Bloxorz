from pathlib import Path

from bloxorz.advanced import AdvancedRuleExtension
from bloxorz.core.enums import Direction, Orientation
from bloxorz.core.game import BloxorzCoreGame
from bloxorz.core.state import BlockState


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_advanced_game(
    filename: str,
) -> BloxorzCoreGame:
    level_path = (
        project_root()
        / "tests"
        / "fixtures"
        / "levels"
        / filename
    )

    rules = AdvancedRuleExtension(
        level_path
    )

    return BloxorzCoreGame.from_level_file(
        level_path,
        rule_extension=rules,
    )


def test_fragile_rules() -> None:
    game = load_advanced_game(
        "level_11_fragile_debug.json"
    )

    # Đứng trên F tại c3 phải invalid.
    standing = BlockState(
        1,
        3,
        Orientation.STANDING,
    )

    assert not game.validate_state(
        standing
    ).valid

    # Nằm ngang qua c2,c3 phải valid.
    lying = BlockState(
        1,
        2,
        Orientation.HORIZONTAL,
    )

    assert game.validate_state(
        lying
    ).valid


def test_soft_switch_opens_bridge() -> None:
    game = load_advanced_game(
        "level_12_soft_bridge_debug.json"
    )

    rules = game.rule_extension

    assert rules.bridge_states[(1, 5)] is False

    first_move = game.move(Direction.RIGHT)

    assert first_move.valid
    assert rules.bridge_states[(1, 5)] is True


def test_heavy_switch_only_works_when_standing() -> None:
    game = load_advanced_game(
        "level_13_heavy_bridge_debug.json"
    )

    rules = game.rule_extension

    assert rules.bridge_states[(1, 5)] is False

    # Sau move đầu, block nằm ở c2,c3.
    assert game.move(Direction.RIGHT).valid
    assert rules.bridge_states[(1, 5)] is False

    # Sau move thứ hai, block đứng tại O ở c4.
    assert game.move(Direction.RIGHT).valid
    assert rules.bridge_states[(1, 5)] is True


def test_closed_and_open_bridge() -> None:
    game = load_advanced_game(
        "level_12_soft_bridge_debug.json"
    )

    rules = game.rule_extension

    bridge_state = BlockState(
        1,
        5,
        Orientation.HORIZONTAL,
    )

    # Cầu đóng: invalid.
    assert not game.validate_state(
        bridge_state
    ).valid

    # Mở cầu thủ công: valid.
    rules.bridge_states[(1, 5)] = True

    assert game.validate_state(
        bridge_state
    ).valid


def test_reset_restores_bridge() -> None:
    game = load_advanced_game(
        "level_12_soft_bridge_debug.json"
    )

    rules = game.rule_extension
    rules.bridge_states[(1, 5)] = True

    game.reset()

    assert rules.bridge_states[(1, 5)] is False
    assert game.move_count == 0
    assert game.state == game.initial_state


if __name__ == "__main__":
    test_fragile_rules()
    test_soft_switch_opens_bridge()
    test_heavy_switch_only_works_when_standing()
    test_closed_and_open_bridge()
    test_reset_restores_bridge()

    print("All advanced tile tests passed.")