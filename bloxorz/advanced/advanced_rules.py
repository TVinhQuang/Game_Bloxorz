from __future__ import annotations

from typing import Hashable

from bloxorz.core.board import Board
from bloxorz.core.enums import Direction
from bloxorz.core.rules import ValidationResult
from bloxorz.core.state import BlockState


class AdvancedRuleExtension:
    """
    Skeleton cho người phụ trách Advanced tiles.

    Chưa implement ở giai đoạn Core.
    Khi làm Advanced, class này sẽ xử lý:
    - fragile tiles
    - bridges
    - soft switch
    - heavy switch
    - split switch
    - split/rejoin block
    """

    def validate_state(self, board: Board, state: BlockState) -> ValidationResult:
        # TODO Advanced:
        # - Nếu đứng trên fragile => invalid.
        # - Nếu đè lên bridge đang đóng => invalid.
        return ValidationResult(valid=True)

    def after_valid_move(
        self,
        board: Board,
        old_state: BlockState,
        direction: Direction,
        new_state: BlockState,
    ) -> BlockState:
        # TODO Advanced:
        # - Nếu đè switch thì toggle/permanent bridge.
        # - Nếu đè split switch thì chuyển qua split mode.
        return new_state

    def state_extra_key(self) -> tuple[Hashable, ...]:
        # TODO Advanced:
        # - Trả về bridge states.
        # - Trả về split states nếu có.
        return ()

    def move_cost(
        self,
        board: Board,
        old_state: BlockState,
        direction: Direction,
        new_state: BlockState,
    ) -> float:
        # TODO Advanced/UCS:
        # - Có thể đổi cost nếu qua fragile/switch/split.
        return 1.0