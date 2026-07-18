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
    Class xử lý các luật nâng cao (Advanced tiles) mở rộng từ Core.
    """
    
    FRAGILE = "F"          # Ô dễ vỡ
    BRIDGE_CLOSED = "B"    # Cầu đang đóng
    BRIDGE_OPEN = "BO"     # Cầu đang mở (dùng riêng cho Renderer vẽ)
    SOFT_SWITCH = "X"      # Công tắc nhẹ
    HEAVY_SWITCH = "O"     # Công tắc nặng

    def __init__(self, level_path: Path | str | None = None):
        self.bridge_states: dict[tuple[int, int], bool] = {}
        self.switches_config: list[dict] = []
        self.bridges_config: list[dict] = []
        self.level_path = level_path
        
        # --- BỘ CHỈ SỐ THEO DÕI ĐỂ TỰ ĐỘNG KHÔI PHỤC KHI RESET ---
        self.initial_state_anchor = None
        self.initial_orientation = None
        self.last_state_anchor = None
        self.needs_reset = False

        # Nếu được truyền đường dẫn file, tự nạp cấu hình trực tiếp từ JSON
        if level_path:
            self._load_config_from_json(level_path)

    def _load_config_from_json(self, level_path: Path | str):
        try:
            with open(level_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.switches_config = data.get("switches", [])
            self.bridges_config = data.get("bridges", [])
            
            # Khởi tạo trạng thái đóng/mở của từng ô cầu
            for b in self.bridges_config:
                r, c = b.get("r"), b.get("c")
                opened = b.get("initially_open", False)
                if r is not None and c is not None:
                    self.bridge_states[(r, c)] = opened
        except Exception as e:
            print(f"[AdvancedRules] Error loading JSON: {e}")

    def reset(self):
        """
        Khôi phục toàn bộ trạng thái cầu đường về mặc định ban đầu.
        """
        if self.level_path:
            self._load_config_from_json(self.level_path)
        self.needs_reset = False
        self.last_state_anchor = None

    def _ensure_initialized(self, board: Board):
        # Đính kèm chính nó vào board để Renderer có thể đọc trạng thái cầu
        board.rule_extension = self

    def validate_state(self, board: Board, state: BlockState) -> ValidationResult:
        """
        Kiểm tra trạng thái khối block ở vị trí mới có hợp lệ không.
        """
        self._ensure_initialized(board)
        
        # Lấy tọa độ mốc (anchor) hiện tại của khối block
        current_anchor = state.anchor if hasattr(state, "anchor") else None
        
        # Ghi lại vị trí xuất phát ban đầu ở frame đầu tiên để làm mốc so sánh
        if self.initial_state_anchor is None and current_anchor is not None:
            self.initial_state_anchor = current_anchor
            self.initial_orientation = state.orientation

        # ====================================================
        # PHÒNG THỦ LỚP 2: TỰ ĐỘNG KHÔI PHỤC KHI CHẾT/RESET THỦ CÔNG
        # ====================================================
        # 1. Nếu lượt đi trước bị phát hiện thua cuộc (needs_reset == True)
        if self.needs_reset:
            self.reset()

        # 2. Nếu phát hiện block "dịch chuyển tức thời" về vị trí xuất phát 
        # (Khoảng cách di chuyển lớn hơn 2 ô gạch -> chắc chắn là người chơi bấm Restart)
        if (
            self.last_state_anchor is not None 
            and self.initial_state_anchor is not None 
            and current_anchor == self.initial_state_anchor
        ):
            dist = abs(current_anchor[0] - self.last_state_anchor[0]) + abs(current_anchor[1] - self.last_state_anchor[1])
            if dist > 2:
                self.reset()

        self.last_state_anchor = current_anchor
        # ====================================================

        cells = state.occupied_cells()
        for r, c in cells:
            tile = board.cell_at(r, c)

            # 1. Xử lý Luật Fragile (Ô dễ vỡ)
            if tile == self.FRAGILE:
                if state.orientation == Orientation.STANDING:
                    self.needs_reset = True  # Đánh dấu thua để reset ở lượt sau
                    return ValidationResult(valid=False, reason="Block broke the fragile tile!")

            # 2. Xử lý Luật Cầu đóng
            if tile == self.BRIDGE_CLOSED:
                if not self.bridge_states.get((r, c), False):
                    self.needs_reset = True  # Đánh dấu thua để reset ở lượt sau
                    return ValidationResult(valid=False, reason="Block fell through a closed bridge!")

        return ValidationResult(valid=True)

    def after_valid_move(
        self,
        board: Board,
        old_state: BlockState,
        direction: Direction,
        new_state: BlockState,
    ) -> BlockState:
        """
        Xử lý sự kiện kích hoạt công tắc sau khi di chuyển hợp lệ.
        """
        cells = new_state.occupied_cells()

        for r, c in cells:
            tile = board.cell_at(r, c)

            # Công tắc nhẹ (Soft Switch): Chạm vào là kích hoạt
            if tile == self.SOFT_SWITCH:
                self._toggle_bridges_linked_to(r, c)

            # Công tắc nặng (Heavy Switch): Chỉ kích hoạt khi đứng thẳng
            elif tile == self.HEAVY_SWITCH:
                if new_state.orientation == Orientation.STANDING:
                    self._toggle_bridges_linked_to(r, c)

        return new_state

    def state_extra_key(self) -> tuple[Hashable, ...]:
        return tuple(self.bridge_states[k] for k in sorted(self.bridge_states.keys()))

    def move_cost(
        self,
        board: Board,
        old_state: BlockState,
        direction: Direction,
        new_state: BlockState,
    ) -> float:
        return 1.0

    def _toggle_bridges_linked_to(self, switch_r: int, switch_c: int):
        """
        Tìm các cầu kết nối với công tắc dựa trên cấu hình JSON trực tiếp.
        """
        for s in self.switches_config:
            s_r, s_c = s.get("r"), s.get("c")

            if s_r == switch_r and s_c == switch_c:
                targets = s.get("targets", [])
                for t_r, t_c in targets:
                    current_state = self.bridge_states.get((t_r, t_c), False)
                    self.bridge_states[(t_r, t_c)] = not current_state

    # ====================================================
    # BẢO VỆ CHO SOLVER (BFS/DFS): Tránh trùng lặp tham chiếu
    # ====================================================
    def __copy__(self):
        new_obj = AdvancedRuleExtension(self.level_path)
        new_obj.bridge_states = self.bridge_states.copy()
        new_obj.switches_config = self.switches_config
        new_obj.bridges_config = self.bridges_config
        new_obj.initial_state_anchor = self.initial_state_anchor
        new_obj.initial_orientation = self.initial_orientation
        new_obj.last_state_anchor = self.last_state_anchor
        new_obj.needs_reset = self.needs_reset
        return new_obj

    def __deepcopy__(self, memo):
        import copy
        new_obj = AdvancedRuleExtension(self.level_path)
        new_obj.bridge_states = copy.deepcopy(self.bridge_states, memo)
        new_obj.switches_config = copy.deepcopy(self.switches_config, memo)
        new_obj.bridges_config = copy.deepcopy(self.bridges_config, memo)
        new_obj.initial_state_anchor = copy.deepcopy(self.initial_state_anchor, memo)
        new_obj.initial_orientation = copy.deepcopy(self.initial_orientation, memo)
        new_obj.last_state_anchor = copy.deepcopy(self.last_state_anchor, memo)
        new_obj.needs_reset = copy.deepcopy(self.needs_reset, memo)
        return new_obj


# ==============================================================================
# PHÒNG THỦ LỚP 1 (MONKEY PATCH): Tự động móc nối vào hàm reset() gốc của Core Game
# ==============================================================================
try:
    game_class = None
    # Tự động truy quét các cấu trúc thư mục khả dĩ để tìm lớp quản lý Game Core
    for module_name in ["bloxorz.core.game", "bloxorz.core", "bloxorz.game"]:
        try:
            import importlib
            mod = importlib.import_module(module_name)
            for attr_name in ["BloxorzCoreGame", "BloxorzGame", "Game"]:
                if hasattr(mod, attr_name):
                    game_class = getattr(mod, attr_name)
                    break
            if game_class:
                break
        except Exception:
            continue

    if game_class and hasattr(game_class, "reset"):
        original_reset = game_class.reset
        
        def patched_reset(self_game, *args, **kwargs):
            result = original_reset(self_game, *args, **kwargs)
            # Nếu game có giữ rule_extension nâng cao, tự động khôi phục cầu đường
            if hasattr(self_game, "rule_extension") and self_game.rule_extension:
                self_game.rule_extension.reset()
            elif hasattr(self_game, "rules") and hasattr(self_game.rules, "reset"):
                self_game.rules.reset()
            return result
            
        game_class.reset = patched_reset
        print("[AdvancedRules] Successfully patched Game.reset for auto-reset!")
except Exception as e:
    print(f"[AdvancedRules] Warning: Could not patch game reset method ({e})")