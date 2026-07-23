from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Protocol

from .board import Board
from .enums import Direction
from .state import BlockState


@dataclass(frozen=True)
class ValidationResult:
    # State có hợp lệ hay không.
    valid: bool

    # Thông báo cho GUI.
    reason: str = ""

    # Mã máy đọc để GUI chọn đúng hiệu ứng.
    # Ví dụ:
    # "unsupported"
    # "fragile_break"
    # "closed_bridge"
    code: str = ""


class RuleExtension(Protocol):
    """
    Protocol cho các luật mở rộng.

    Core không implement fragile/bridge/switch/split ở đây.
    Người phụ trách Advanced sẽ tạo class riêng implement protocol này.

    Ví dụ sau này:
        AdvancedRuleExtension(RuleExtension)
    """

    def validate_state(self, board: Board, state: BlockState) -> ValidationResult:
        """
        Kiểm tra state theo luật mở rộng.

        Advanced sẽ dùng hàm này để kiểm tra:
        - block đứng trên fragile thì invalid
        - block nằm trên bridge đóng thì invalid
        - split block rules

        Core chỉ định nghĩa protocol.
        """

        ...

    def after_valid_move(
        self,
        board: Board,
        old_state: BlockState,
        direction: Direction,
        new_state: BlockState,
    ) -> BlockState:
        """
        Hook chạy sau khi move hợp lệ theo luật Core.

        Advanced sẽ dùng hàm này để:
        - toggle bridge khi đè switch
        - activate heavy switch
        - split block
        - merge block

        Core chỉ định nghĩa protocol.
        """

        ...

    def state_extra_key(self) -> tuple[Hashable, ...]:
        """
        Trả về phần state bổ sung cho solver.

        Advanced cần dùng để thêm:
        - bridge states
        - split mode
        - active cube
        - cube positions

        Core chỉ định nghĩa protocol.
        """

        ...

    def move_cost(
        self,
        board: Board,
        old_state: BlockState,
        direction: Direction,
        new_state: BlockState,
    ) -> float:
        """
        Trả về cost của một move.

        UCS/A* sau này có thể dùng.
        Core mặc định mỗi move cost = 1.
        Advanced có thể tăng cost khi qua fragile/split/switch.
        """

        ...
        
    def reset(self) -> None:
        """
        Khôi phục trạng thái nội bộ của rule extension.

        AdvancedRuleExtension dùng hàm này để đưa cầu
        về trạng thái ban đầu khi restart level.
        """
        ...


class NoOpRuleExtension:
    """
    RuleExtension mặc định cho Core.

    Class này không thêm luật gì cả.
    Nó giúp Core chạy được ngay cả khi Advanced chưa làm.
    """

    def validate_state(self, board: Board, state: BlockState) -> ValidationResult:
        # Core không có luật phụ, nên luôn hợp lệ.
        return ValidationResult(valid=True)

    def after_valid_move(
        self,
        board: Board,
        old_state: BlockState,
        direction: Direction,
        new_state: BlockState,
    ) -> BlockState:
        # Core không làm gì sau move, trả lại new_state y nguyên.
        return new_state

    def state_extra_key(self) -> tuple[Hashable, ...]:
        # Core không có bridge/split state.
        return ()

    def move_cost(
        self,
        board: Board,
        old_state: BlockState,
        direction: Direction,
        new_state: BlockState,
    ) -> float:
        # Core mặc định mỗi lần lăn có cost = 1.
        return 1.0
    
    def reset(self) -> None:
        """
        Core-only level không có trạng thái Advanced cần reset.
        """

        return None