from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from .movement import compute_next_state

from .board import Board
from .enums import DIRECTION_ORDER, Direction, MoveStatus, Orientation
from .movement import compute_next_state
from .rules import NoOpRuleExtension, RuleExtension, ValidationResult
from .state import BlockState, GameStateKey


@dataclass(frozen=True)
class MoveResult:
    """
    Kết quả của một lần gọi move().
    """

    status: MoveStatus
    old_state: BlockState
    new_state: BlockState
    valid: bool
    won: bool
    message: str
    
    # State mà block đã cố di chuyển tới.
    # Với move hợp lệ, nó bằng new_state.
    # Với move lỗi, nó vẫn giúp GUI vẽ hiệu ứng.
    attempted_state: BlockState | None = None

    # Mã lỗi lấy từ ValidationResult.
    failure_code: str = ""


@dataclass(frozen=True)
class Successor:
    """
    Một successor dùng cho solver sau này.

    action: hướng di chuyển
    state: state sau khi đi action
    cost: chi phí move
    """

    action: Direction
    state: BlockState
    cost: float


class BloxorzCoreGame:
    """
    Game engine cho phần Core mechanics.

    Class này xử lý:
    - reset
    - move
    - legal actions
    - illegal move detection
    - win detection
    - encode state cho solver

    Class này KHÔNG xử lý:
    - GUI rendering
    - BFS/DFS/UCS/A*
    - fragile/bridge/switch/split

    Các phần đó sẽ dùng hook hoặc subclass sau.
    """

    def __init__(
        self,
        board: Board,
        rule_extension: RuleExtension | None = None,
    ):
        # Board chứa layout của level.
        self.board = board

        # Nếu chưa có Advanced rules thì dùng NoOp.
        self.rule_extension = rule_extension or NoOpRuleExtension()
        
        # Renderer cần truy cập bridge state hiện tại.
        setattr(
            self.board,
            "rule_extension",
            self.rule_extension,
        )

        # Block luôn bắt đầu ở S và đứng thẳng.
        self.initial_state = BlockState(
            r=board.start[0],
            c=board.start[1],
            orientation=Orientation.STANDING,
        )

        # State hiện tại của game.
        self.state = self.initial_state
        # Đếm số move hợp lệ người chơi đã đi trong level hiện tại.
        # Invalid move không được tính.
        self.move_count = 0
        
    @classmethod
    def from_level_file(
        cls,
        level_path: str | Path,
        rule_extension: RuleExtension | None = None,
    ) -> "BloxorzCoreGame":
        # Load board từ file level JSON.
        board = Board.from_level_file(str(level_path))

        # Tạo game từ board.
        return cls(board=board, rule_extension=rule_extension)

    def reset(self) -> None:
        """
        Reset block, move counter và Advanced states.
        """

        self.state = self.initial_state
        self.move_count = 0

        reset_hook = getattr(
            self.rule_extension,
            "reset",
            None,
        )

        if callable(reset_hook):
            reset_hook()

    def encode_state(self, state: BlockState | None = None) -> GameStateKey:
        """
        Encode state thành key hashable để solver dùng.

        Core:
            key = (r, c, orientation)

        Advanced sau này:
            key = (r, c, orientation, bridge states, split states, ...)
        """

        chosen_state = state or self.state

        return GameStateKey(
            block_key=chosen_state.to_key(),
            extra=self.rule_extension.state_extra_key(),
        )

    def is_goal_state(self, state: BlockState | None = None) -> bool:
        """
        Kiểm tra win condition.

        Theo đề:
        - Chỉ thắng khi block standing upright trên goal.
        - Nếu block nằm ngang/dọc đè qua goal thì chưa thắng.
        """

        chosen_state = state or self.state

        return (
            chosen_state.orientation == Orientation.STANDING
            and self.board.is_goal_cell(chosen_state.r, chosen_state.c)
        )

    def validate_core_support(
        self,
        state: BlockState,
    ) -> ValidationResult:
        """
        Kiểm tra toàn bộ các ô mà block đang chiếm.

        Nếu bất kỳ phần nào của block:
        - ra khỏi board; hoặc
        - nằm trên void

        thì state không hợp lệ.
        """

        for r, c in state.occupied_cells():
            if not self.board.is_base_support_cell(r, c):
                return ValidationResult(
                    valid=False,
                    reason=(
                        f"Block is not fully supported "
                        f"at cell ({r}, {c})."
                    ),
                    code="unsupported",
                )

        return ValidationResult(valid=True)

    def validate_state(self, state: BlockState) -> ValidationResult:
        """
        Kiểm tra state bằng Core rules trước, sau đó đến extension rules.

        Thứ tự này quan trọng:
        1. Core kiểm tra ra ngoài board/void.
        2. Advanced kiểm tra fragile/bridge/switch/split nếu có.
        """

        core_result = self.validate_core_support(state)

        if not core_result.valid:
            return core_result

        extension_result = self.rule_extension.validate_state(self.board, state)

        if not extension_result.valid:
            return extension_result

        return ValidationResult(valid=True)

    def next_state_if_valid(
        self,
        state: BlockState,
        direction: Direction,
    ) -> BlockState | None:
        """
        Tính next state nếu move hợp lệ.

        Nếu move invalid thì trả None.
        """

        raw_next_state = compute_next_state(state, direction)

        validation = self.validate_state(raw_next_state)

        if not validation.valid:
            return None

        final_next_state = self.rule_extension.after_valid_move(
            board=self.board,
            old_state=state,
            direction=direction,
            new_state=raw_next_state,
        )

        return final_next_state

    def move(self, direction: Direction) -> MoveResult:
        """
        Di chuyển block và giữ lại nguyên nhân nếu move thất bại.
        """

        old_state = self.state

        # State hình học mà block cố lăn tới.
        raw_next_state = compute_next_state(
            old_state,
            direction,
        )

        # Kiểm tra Core + Advanced.
        validation = self.validate_state(
            raw_next_state
        )

        if not validation.valid:
            return MoveResult(
                status=MoveStatus.INVALID,
                old_state=old_state,
                new_state=old_state,
                valid=False,
                won=self.is_goal_state(old_state),
                message=(
                    validation.reason
                    or f"Invalid move: {direction.value}"
                ),
                attempted_state=raw_next_state,
                failure_code=validation.code,
            )

        # Áp dụng switch/bridge sau khi state hợp lệ.
        final_next_state = (
            self.rule_extension.after_valid_move(
                board=self.board,
                old_state=old_state,
                direction=direction,
                new_state=raw_next_state,
            )
        )

        self.state = final_next_state
        self.move_count += 1

        if self.is_goal_state(final_next_state):
            return MoveResult(
                status=MoveStatus.WON,
                old_state=old_state,
                new_state=final_next_state,
                valid=True,
                won=True,
                message="You win!",
                attempted_state=final_next_state,
            )

        return MoveResult(
            status=MoveStatus.MOVED,
            old_state=old_state,
            new_state=final_next_state,
            valid=True,
            won=False,
            message=f"Moved: {direction.value}",
            attempted_state=final_next_state,
        )

    def legal_actions(self, state: BlockState | None = None) -> list[Direction]:
        """
        Trả về danh sách action hợp lệ từ state hiện tại.

        Hàm này sẽ được GUI và solver dùng lại.
        """

        chosen_state = state or self.state
        actions: list[Direction] = []

        for direction in DIRECTION_ORDER:
            if self.next_state_if_valid(chosen_state, direction) is not None:
                actions.append(direction)

        return actions

    def successors(self, state: BlockState | None = None) -> list[Successor]:
        """
        Trả về tất cả successor hợp lệ từ một state.

        BFS/DFS/UCS/A* sau này sẽ dùng hàm này.
        """

        chosen_state = state or self.state
        result: list[Successor] = []

        for direction in DIRECTION_ORDER:
            next_state = self.next_state_if_valid(chosen_state, direction)

            if next_state is None:
                continue

            cost = self.rule_extension.move_cost(
                board=self.board,
                old_state=chosen_state,
                direction=direction,
                new_state=next_state,
            )

            result.append(
                Successor(
                    action=direction,
                    state=next_state,
                    cost=cost,
                )
            )

        return result