from __future__ import annotations

import json
from pathlib import Path
from typing import Hashable

from bloxorz.core.board import Board
from bloxorz.core.enums import Direction, Orientation
from bloxorz.core.rules import ValidationResult
from bloxorz.core.state import BlockState


class AdvancedRuleExtension:
    """
    Luật cho các Advanced tiles hiện đã được triển khai:

    F = Fragile tile
    B = Bridge tile
    X = Soft switch
    O = Heavy switch

    Split switch và split cubes chưa được xử lý ở giai đoạn này.
    """

    FRAGILE = "F"
    BRIDGE = "B"
    SOFT_SWITCH = "X"
    HEAVY_SWITCH = "O"

    def __init__(
        self,
        level_path: str | Path | None = None,
    ) -> None:
        # False: cầu đóng, không đỡ được block.
        # True: cầu mở, đỡ được block.
        self.bridge_states: dict[
            tuple[int, int],
            bool,
        ] = {}

        self.switches_config: list[dict] = []
        self.bridges_config: list[dict] = []

        self.level_path = (
            Path(level_path)
            if level_path is not None
            else None
        )

        if self.level_path is not None:
            self._load_config_from_json(
                self.level_path
            )

    def _load_config_from_json(
        self,
        level_path: str | Path,
    ) -> None:
        """
        Đọc bridge/switch configuration từ level JSON.
        """

        path = Path(level_path)

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        self.switches_config = list(
            data.get("switches", [])
        )

        self.bridges_config = list(
            data.get("bridges", [])
        )

        # Không giữ bridge state của lần load trước.
        self.bridge_states.clear()

        for bridge in self.bridges_config:
            r = bridge.get("r")
            c = bridge.get("c")

            if r is None or c is None:
                continue

            # Hỗ trợ cả hai tên field để tránh lệch format JSON.
            initially_open = bool(
                bridge.get(
                    "initially_open",
                    bridge.get(
                        "initial_open",
                        False,
                    ),
                )
            )

            self.bridge_states[
                (int(r), int(c))
            ] = initially_open

    def reset(self) -> None:
        """
        Đưa tất cả cầu về trạng thái ban đầu của level.
        """

        self.bridge_states.clear()
        self.switches_config.clear()
        self.bridges_config.clear()

        if self.level_path is not None:
            self._load_config_from_json(
                self.level_path
            )

    def validate_state(
        self,
        board: Board,
        state: BlockState,
    ) -> ValidationResult:
        """
        Kiểm tra các luật của Advanced tiles.

        Core đã kiểm tra:
        - block ra ngoài board;
        - block nằm trên void.

        Hàm này kiểm tra thêm:
        - block đứng trên fragile tile;
        - block nằm trên bridge đang đóng.
        """

        # Kiểm tra từng ô mà block đang chiếm.
        for r, c in state.occupied_cells():
            # Đọc loại tile tại vị trí hiện tại.
            tile = board.cell_at(r, c)

            # ====================================================
            # FRAGILE TILE
            # ====================================================

            # Fragile chỉ vỡ khi block đứng thẳng trên nó.
            # Nếu block đang nằm ngang/dọc thì vẫn hợp lệ.
            if (
                tile == self.FRAGILE
                and state.orientation == Orientation.STANDING
            ):
                return ValidationResult(
                    valid=False,
                    reason="The fragile tile shattered.",

                    # GUI đọc mã này để chạy hiệu ứng:
                    # tile vỡ trước, sau đó block mới rơi.
                    code="fragile_break",
                )

            # ====================================================
            # BRIDGE
            # ====================================================

            # Kiểm tra nếu ô hiện tại là bridge.
            if tile == self.BRIDGE:
                # Đọc trạng thái mở/đóng của bridge.
                # Nếu không tìm thấy thì mặc định là đóng.
                bridge_is_open = self.bridge_states.get(
                    (r, c),
                    False,
                )

                # Bridge đóng không thể đỡ block.
                if not bridge_is_open:
                    return ValidationResult(
                        valid=False,
                        reason=(
                            "The block fell through "
                            "a closed bridge."
                        ),

                        # GUI đọc mã này để chạy hiệu ứng
                        # rơi qua khoảng trống của bridge.
                        code="closed_bridge",
                    )

        # Không vi phạm luật Advanced nào.
        return ValidationResult(
            valid=True,
        )

    def after_valid_move(
        self,
        board: Board,
        old_state: BlockState,
        direction: Direction,
        new_state: BlockState,
    ) -> BlockState:
        """
        Kích hoạt switch sau khi block đã di chuyển hợp lệ.
        """

        old_cells = set(
            old_state.occupied_cells()
        )

        new_cells = set(
            new_state.occupied_cells()
        )

        for r, c in new_cells:
            tile = board.cell_at(r, c)

            # Soft switch:
            # bất kỳ phần nào của block chạm vào đều kích hoạt.
            if tile == self.SOFT_SWITCH:
                # Chỉ kích hoạt khi vừa mới đè lên switch,
                # tránh toggle liên tục khi block vẫn ở trên đó.
                if (r, c) not in old_cells:
                    self._activate_switch(r, c)

            # Heavy switch:
            # chỉ được nhấn khi block đứng thẳng.
            elif (
                tile == self.HEAVY_SWITCH
                and new_state.orientation
                == Orientation.STANDING
            ):
                old_was_pressing = (
                    old_state.orientation
                    == Orientation.STANDING
                    and (r, c) in old_cells
                )

                if not old_was_pressing:
                    self._activate_switch(r, c)

        return new_state

    def _activate_switch(
        self,
        switch_r: int,
        switch_c: int,
    ) -> None:
        """
        Thực hiện effect của switch được khai báo trong JSON.

        effect hỗ trợ:
        - toggle
        - open
        - close

        Nếu không khai báo effect thì mặc định là toggle.
        """

        for switch in self.switches_config:
            configured_r = switch.get("r")
            configured_c = switch.get("c")

            if (
                configured_r != switch_r
                or configured_c != switch_c
            ):
                continue

            effect = str(
                switch.get(
                    "effect",
                    "toggle",
                )
            ).lower()

            targets = switch.get(
                "targets",
                [],
            )

            for target in targets:
                if not isinstance(target, (list, tuple)):
                    continue

                if len(target) != 2:
                    continue

                target_r = int(target[0])
                target_c = int(target[1])
                position = (target_r, target_c)

                current = self.bridge_states.get(
                    position,
                    False,
                )

                if effect == "toggle":
                    self.bridge_states[position] = not current

                elif effect in (
                    "open",
                    "on",
                    "permanent_open",
                ):
                    self.bridge_states[position] = True

                elif effect in (
                    "close",
                    "off",
                    "permanent_close",
                ):
                    self.bridge_states[position] = False

                else:
                    raise ValueError(
                        f"Unknown switch effect: {effect}"
                    )

    def state_extra_key(
        self,
    ) -> tuple[Hashable, ...]:
        """
        Đưa bridge configuration vào state key.

        Cùng vị trí block nhưng bridge mở/đóng khác nhau
        phải là hai state khác nhau.
        """

        return tuple(
            (
                position,
                self.bridge_states[position],
            )
            for position in sorted(
                self.bridge_states
            )
        )

    def move_cost(
        self,
        board: Board,
        old_state: BlockState,
        direction: Direction,
        new_state: BlockState,
    ) -> float:
        # Giai đoạn này tất cả move có cost bằng 1.
        return 1.0