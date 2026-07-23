from __future__ import annotations

from pathlib import Path

from bloxorz.core.state import BlockState

from bloxorz.core.movement import compute_next_state

import pygame

from bloxorz.core.enums import Direction
from bloxorz.core.game import BloxorzCoreGame

from . import theme
from .buttons import Button
from .renderer import Renderer

from bloxorz.solvers import (
    solve_astar,
    solve_bfs,
    solve_dfs,
    solve_ucs,
)
from bloxorz.solvers.base import SolverResult


class BloxorzPygameApp:
    """
    App Pygame chính cho Bloxorz.

    Nhiệm vụ:
    - Load level
    - Tạo BloxorzCoreGame
    - Bắt event keyboard/mouse
    - Gọi game.move()
    - Gọi renderer để vẽ
    """

    def __init__(self) -> None:
        # Khởi tạo pygame.
        pygame.init()

        # Tạo cửa sổ game.
        self.screen = pygame.display.set_mode(
            (theme.WINDOW_WIDTH, theme.WINDOW_HEIGHT)
        )

        # Đặt caption cửa sổ.
        pygame.display.set_caption("Bloxorz Solver - Core Mechanics")

        # Clock dùng để giữ FPS ổn định.
        self.clock = pygame.time.Clock()

        # Renderer chịu trách nhiệm vẽ.
        self.renderer = Renderer()

        # Source root là thư mục Source/.
        self.source_root = Path(__file__).resolve().parents[2]

        # Thư mục levels.
        self.levels_dir = self.source_root / "levels"

        # Load danh sách level JSON.
        self.level_paths = self.load_level_paths()

        # Index level hiện tại.
        self.current_level_index = 0

        # Game hiện tại.
        self.game = self.create_game(self.current_level_index)

        # Message hiển thị trên panel.
        self.message = "Use WASD or arrow keys to move."

        # Loại message: info/error/success.
        self.message_type = "info"

        # App có đang chạy không.
        self.running = True

        # Queue lưu các hướng người chơi bấm trong lúc animation đang chạy.
        # Giúp bấm nhanh không bị mất input.
        self.input_queue: list[Direction] = []
        
        # Lưu các phím di chuyển đang được giữ.
        # Dùng để tránh giữ phím tạo nhiều move liên tục.
        self.held_move_keys: set[int] = set()

        # Animation state.
        self.is_animating = False

        # State bắt đầu animation.
        self.animation_from: BlockState | None = None

        # State kết thúc animation.
        self.animation_to: BlockState | None = None

        # Thời điểm bắt đầu animation, tính bằng pygame time.
        self.animation_start_time = 0

        # State tạm để renderer vẽ trong lúc animation.
        self.display_state: BlockState | None = None
        
        # Falling effect state.
        # None: không có hiệu ứng rơi.
        # "block": block đang rơi.
        # "tiles": các tile đang rơi.
        self.fall_phase: str | None = None

        # Thời điểm bắt đầu phase rơi hiện tại.
        self.fall_start_time = 0

        # State dùng để vẽ block rơi.
        self.falling_block_state: BlockState | None = None

        # Offset y hiện tại của block khi rơi.
        self.block_fall_y_offset = 0

        # Danh sách tile sẽ rơi.
        self.falling_tiles: list[tuple[int, int]] = []

        # Offset y hiện tại của từng tile.
        self.tile_fall_offsets: dict[tuple[int, int], int] = {}
        
        # Tạo danh sách button.
        self.buttons = self.create_buttons()
        
        # Queue chứa solution do solver trả về.
        self.solver_action_queue: list[Direction] = []

        # Có đang tự động phát lời giải hay không.
        self.is_solver_playback = False

        # Kết quả solver gần nhất để hiển thị metrics.
        self.last_solver_result: SolverResult | None = None
        
        # True khi người chơi hoặc solver vừa hoàn thành level.
        self.auto_level_advance_pending = False

        # Thời điểm bắt đầu đếm thời gian chờ chuyển level.
        # Giá trị 0 nghĩa là chưa bắt đầu đếm.
        self.auto_level_advance_start_time = 0
        
        # ---------------- LEVEL TRANSITION ----------------

        # Phase hiện tại:
        # None       = không chuyển màn
        # "fade_out" = màn hình đang tối dần
        # "hold"     = giữ màn hình tối
        # "fade_in"  = level mới đang hiện dần lên
        self.level_transition_phase: str | None = None

        # Thời điểm bắt đầu phase hiện tại.
        self.level_transition_start_time = 0

        # Alpha của lớp phủ chuyển màn.
        self.level_transition_alpha = 0

        # Index của level sẽ được load.
        self.transition_target_level_index: int | None = None

        # Nội dung chữ hiện trên màn chuyển level.
        self.transition_title = ""
        self.transition_subtitle = ""
        
    def is_level_transition_active(self) -> bool:
        """
        Kiểm tra app có đang thực hiện hiệu ứng chuyển level không.
        """

        return self.level_transition_phase is not None
    
    def transition_smoothstep(self, t: float) -> float:
        """
        Làm chuyển động fade mềm hơn nội suy tuyến tính.

        Input và output đều trong đoạn [0, 1].
        """

        t = max(0.0, min(1.0, t))

        return t * t * (3.0 - 2.0 * t)
    
    def start_level_transition(self, target_level_index: int) -> None:
        """
        Bắt đầu hiệu ứng chuyển sang một level khác.

        Level chưa được load ngay.
        Ta đợi màn hình fade-out hoàn toàn rồi mới load,
        nhờ đó người chơi không nhìn thấy board đổi đột ngột.
        """

        # Không bắt đầu thêm một transition nếu transition khác đang chạy.
        if self.is_level_transition_active():
            return

        # Bảo vệ index.
        if not 0 <= target_level_index < len(self.level_paths):
            return

        self.transition_target_level_index = target_level_index

        self.level_transition_phase = "fade_out"
        self.level_transition_start_time = pygame.time.get_ticks()
        self.level_transition_alpha = 0

        # Trong lúc fade-out, hiển thị level vừa hoàn thành.
        self.transition_title = "LEVEL COMPLETE"
        self.transition_subtitle = (
            f"Level {self.game.board.id}: {self.game.board.name}"
        )

        # Không nhận input cũ trong lúc chuyển màn.
        self.clear_animation_and_input_queue()
        self.clear_solver_playback()
        
    def load_level_immediately(self, level_index: int) -> None:
        """
        Load một level ngay lập tức.

        Hàm này chỉ dùng bên trong transition.
        Không tự tạo thêm transition mới.
        """

        self.current_level_index = level_index
        self.game = self.create_game(level_index)

        self.clear_animation_and_input_queue()
        self.clear_solver_playback()

        self.last_solver_result = None

        self.message = f"Loaded level {self.game.board.id}."
        self.message_type = "info"
        
    def update_level_transition(self) -> None:
        """
        Cập nhật hiệu ứng chuyển level theo ba phase:

        1. fade_out:
        Level cũ tối dần.

        2. hold:
        Load level mới và giữ màn hình tối.

        3. fade_in:
        Level mới hiện dần lên.
        """

        if not self.is_level_transition_active():
            return

        now = pygame.time.get_ticks()

        elapsed_seconds = (
            now - self.level_transition_start_time
        ) / 1000.0

        # ---------------- FADE OUT ----------------
        if self.level_transition_phase == "fade_out":
            duration = theme.LEVEL_TRANSITION_FADE_OUT_DURATION

            t = elapsed_seconds / duration
            eased_t = self.transition_smoothstep(t)

            self.level_transition_alpha = int(255 * eased_t)

            if t >= 1.0:
                self.level_transition_alpha = 255

                # Chưa load level mới ngay.
                # Giữ chữ LEVEL COMPLETE trước.
                self.level_transition_phase = "hold_complete"
                self.level_transition_start_time = now

            return

        # ---------------- HOLD ----------------
        if self.level_transition_phase == "hold_complete":
            self.level_transition_alpha = 255

            if elapsed_seconds >= theme.LEVEL_COMPLETE_HOLD_DURATION:
                target_index = self.transition_target_level_index

                if target_index is None:
                    self.finish_level_transition()
                    return

                # Sau khi đã giữ LEVEL COMPLETE đủ lâu,
                # mới load level tiếp theo.
                self.load_level_immediately(target_index)

                # Đổi chữ sang thông tin level mới.
                self.transition_title = f"LEVEL {self.game.board.id}"
                self.transition_subtitle = self.game.board.name

                self.level_transition_phase = "hold_next"
                self.level_transition_start_time = now

            return
        
        if self.level_transition_phase == "hold_next":
            self.level_transition_alpha = 255

            if elapsed_seconds >= theme.NEXT_LEVEL_HOLD_DURATION:
                self.level_transition_phase = "fade_in"
                self.level_transition_start_time = now

            return

        # ---------------- FADE IN ----------------
        if self.level_transition_phase == "fade_in":
            duration = theme.LEVEL_TRANSITION_FADE_IN_DURATION

            t = elapsed_seconds / duration
            eased_t = self.transition_smoothstep(t)

            self.level_transition_alpha = int(
                255 * (1.0 - eased_t)
            )

            if t >= 1.0:
                self.finish_level_transition()

            return
        
    def finish_level_transition(self) -> None:
        """
        Đưa app về trạng thái chơi bình thường sau transition.
        """

        self.level_transition_phase = None
        self.level_transition_start_time = 0
        self.level_transition_alpha = 0
        self.transition_target_level_index = None
        self.transition_title = ""
        self.transition_subtitle = ""

        self.message = (
            f"Level {self.game.board.id}: "
            f"{self.game.board.name}"
        )
        self.message_type = "info"
    
    def schedule_auto_level_advance(self) -> None:
        """
        Đánh dấu rằng level hiện tại đã hoàn thành.

        Đồng hồ chưa bắt đầu ngay vì cần đợi animation
        của nước thắng chạy xong.
        """

        self.auto_level_advance_pending = True
        self.auto_level_advance_start_time = 0
        
    def cancel_auto_level_advance(self) -> None:
        """
        Hủy yêu cầu tự động chuyển level.

        Dùng khi restart, chuyển level thủ công hoặc quit.
        """

        self.auto_level_advance_pending = False
        self.auto_level_advance_start_time = 0
        
    def update_auto_level_advance(self) -> None:
        """
        Chuyển sang level tiếp theo sau khi:
        - đã thắng;
        - animation cuối đã hoàn tất;
        - solver playback đã kết thúc;
        - đã chờ đủ AUTO_NEXT_LEVEL_DELAY.
        """

        if not self.auto_level_advance_pending:
            return

        # Phải đợi animation nước cuối kết thúc.
        if self.is_animating:
            return

        # Không chuyển level trong lúc đang chạy hiệu ứng rơi.
        if self.is_fall_effect_active():
            return

        # Nếu solver còn action thì chưa kết thúc playback.
        if self.is_solver_playback:
            return

        now = pygame.time.get_ticks()

        # Bắt đầu đếm thời gian sau khi mọi animation hoàn tất.
        if self.auto_level_advance_start_time == 0:
            self.auto_level_advance_start_time = now
            return

        elapsed_seconds = (
            now - self.auto_level_advance_start_time
        ) / 1000.0

        if elapsed_seconds < theme.AUTO_NEXT_LEVEL_DELAY:
            return

        # Xóa pending trước khi chuyển level để tránh gọi lặp.
        self.cancel_auto_level_advance()

        # Nếu đã ở level cuối cùng.
        if self.current_level_index >= len(self.level_paths) - 1:
            self.message = "Congratulations! All levels completed!"
            self.message_type = "success"
            return

        next_level_index = self.current_level_index + 1
        
        self.start_level_transition(next_level_index)
    
    def ease_in_quad(self, t: float) -> float:
        """
        Easing cho hiệu ứng rơi.

        t từ 0 đến 1.
        t^2 tạo cảm giác vật rơi nhanh dần.
        """

        t = max(0.0, min(1.0, t))
        return t * t
    
    def is_fall_effect_active(self) -> bool:
        """
        Kiểm tra app có đang chạy hiệu ứng rơi không.
        """

        return self.fall_phase is not None
    
    def start_fall_sequence(self, direction: Direction) -> None:
        """
        Bắt đầu chuỗi hiệu ứng khi người chơi đi nước invalid.

        Phase 1:
            Block rơi xuống khỏi địa hình.

        Phase 2:
            Các tile lần lượt rơi xuống.

        Phase 3:
            Reset level.
        """

        self.clear_animation_and_input_queue()

        # Tính vị trí block sau khi cố lăn theo hướng invalid.
        # Core không chấp nhận state này, nhưng GUI dùng nó để vẽ block đang rơi.
        self.falling_block_state = compute_next_state(self.game.state, direction)

        self.block_fall_y_offset = 0
        self.tile_fall_offsets = {}

        self.fall_phase = "block"
        self.fall_start_time = pygame.time.get_ticks()

        self.message = "The block fell off the map!"
        self.message_type = "error"
        
    def start_tiles_fall_phase(self) -> None:
        """
        Bắt đầu phase các tile của map rơi xuống.

        Ta lấy tất cả tile không phải void.
        Sắp xếp theo r + c để tạo cảm giác rơi lan dần theo mặt isometric.
        """

        self.fall_phase = "tiles"
        self.fall_start_time = pygame.time.get_ticks()

        self.falling_tiles = []

        for r in range(self.game.board.rows):
            for c in range(self.game.board.cols):
                if not self.game.board.is_void_cell(r, c):
                    self.falling_tiles.append((r, c))

        self.falling_tiles.sort(key=lambda cell: cell[0] + cell[1])

        self.tile_fall_offsets = {
            cell: 0 for cell in self.falling_tiles
        }

        self.message = "Resetting level..."
        self.message_type = "error"
        
    def update_fall_effect(self) -> None:
        """
        Update hiệu ứng rơi mỗi frame.
        """

        if self.fall_phase is None:
            return

        now = pygame.time.get_ticks()
        elapsed = (now - self.fall_start_time) / 1000.0

        if self.fall_phase == "block":
            t = elapsed / theme.BLOCK_FALL_DURATION

            eased = self.ease_in_quad(t)

            self.block_fall_y_offset = int(eased * theme.FALL_DISTANCE)

            if t >= 1.0:
                self.block_fall_y_offset = theme.FALL_DISTANCE
                self.start_tiles_fall_phase()

            return

        if self.fall_phase == "tiles":
            max_finish_time = 0.0

            for index, cell in enumerate(self.falling_tiles):
                delay = index * theme.TILE_FALL_STAGGER

                local_t = (elapsed - delay) / theme.TILE_FALL_DURATION

                eased = self.ease_in_quad(local_t)

                self.tile_fall_offsets[cell] = int(eased * theme.FALL_DISTANCE)

                finish_time = delay + theme.TILE_FALL_DURATION
                max_finish_time = max(max_finish_time, finish_time)

            if elapsed >= max_finish_time + theme.RESET_AFTER_FALL_DELAY:
                self.finish_fall_sequence()

            return
        
    def finish_fall_sequence(self) -> None:
        """
        Kết thúc hiệu ứng rơi và reset level hiện tại.
        """

        self.fall_phase = None
        self.fall_start_time = 0
        self.falling_block_state = None
        self.block_fall_y_offset = 0
        self.falling_tiles = []
        self.tile_fall_offsets = {}

        self.game.reset()

        self.message = "Level reset."
        self.message_type = "info"

    def load_level_paths(self) -> list[Path]:
        """
        Load tất cả file level_*.json trong thư mục levels/.

        Ta sort theo tên file để level_01, level_02, ...
        đúng thứ tự.
        """

        level_paths = sorted(self.levels_dir.glob("level_*.json"))

        if not level_paths:
            raise FileNotFoundError(f"No level_*.json files found in {self.levels_dir}")

        return level_paths

    def create_game(self, level_index: int) -> BloxorzCoreGame:
        """
        Tạo game mới từ level index.
        """

        level_path = self.level_paths[level_index]

        return BloxorzCoreGame.from_level_file(level_path)

    def create_buttons(self) -> list[Button]:
        """
        Tạo các button bên panel phải.

        Ta đặt nhóm button ở gần đáy panel và giảm chiều cao button
        để tránh bị chồng lên phần Controls.
        """

        panel_x = theme.WINDOW_WIDTH - theme.SIDE_PANEL_WIDTH

        x = panel_x + 20
        width = theme.SIDE_PANEL_WIDTH - 40
        height = theme.BUTTON_HEIGHT
        gap = theme.BUTTON_GAP

        # 8 button: Restart, Prev, Next, BFS, DFS, UCS, A*, Quit.
        button_count = 8

        # Căn nhóm button sát đáy nhưng vẫn chừa 18px.
        y = theme.WINDOW_HEIGHT - button_count * height - (button_count - 1) * gap - 18

        return [
            Button(pygame.Rect(x, y, width, height), "Restart", "restart"),
            Button(pygame.Rect(x, y + 1 * (height + gap), width, height), "Previous Level", "prev_level"),
            Button(pygame.Rect(x, y + 2 * (height + gap), width, height), "Next Level", "next_level"),
            Button(pygame.Rect(x, y + 3 * (height + gap), width, height), "Solve BFS", "solve_bfs"),
            Button(pygame.Rect(x, y + 4 * (height + gap), width, height), "Solve DFS", "solve_dfs"),
            Button(pygame.Rect(x, y + 5 * (height + gap), width, height), "Solve UCS", "solve_ucs"),
            Button(pygame.Rect(x, y + 6 * (height + gap), width, height), "Solve A*", "solve_astar"),
            Button(pygame.Rect(x, y + 7 * (height + gap), width, height), "Quit", "quit"),
        ]

    def run(self) -> None:
        """
        Game loop chính.

        Mỗi frame:
        1. Bắt event.
        2. Update animation.
        3. Nếu hết animation thì xử lý input đang chờ.
        4. Vẽ lại màn hình.
        """

        while self.running:
            self.handle_events()
            self.update_animation()
            self.update_fall_effect()

            # Chỉ phát solver/input khi không rơi và không chuyển level.
            if (
                not self.is_fall_effect_active()
                and not self.is_level_transition_active()
            ):
                if self.is_solver_playback:
                    self.process_solver_playback()
                else:
                    self.process_queued_input_if_possible()

            # Kiểm tra có cần tự động sang level kế tiếp hay không.
            self.update_auto_level_advance()
            
            # Update transition sau auto-next,
            # vì auto-next có thể vừa bắt đầu transition trong frame này.
            self.update_level_transition()
            
            self.draw()
            self.clock.tick(theme.FPS)

        pygame.quit()

    def handle_events(self) -> None:
        """
        Xử lý toàn bộ event Pygame.
        """

        for event in pygame.event.get():
            # Nếu người dùng bấm nút X của cửa sổ.
            if event.type == pygame.QUIT:
                self.running = False

            # Nếu người dùng bấm phím.
            elif event.type == pygame.KEYDOWN:
                self.handle_key_down(event.key)
                
            elif event.type == pygame.KEYUP:
                self.handle_key_up(event.key)

            # Nếu người dùng click chuột.
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_mouse_click(event.pos)

    def handle_key_up(self, key: int) -> None:
        """
        Khi người chơi thả phím, xóa phím đó khỏi held_move_keys.

        Nhờ vậy mỗi lần nhấn phím chỉ tạo đúng 1 move.
        Muốn đi tiếp thì phải thả ra rồi bấm lại.
        """

        self.held_move_keys.discard(key)

    def handle_key_down(self, key: int) -> None:
        """
        Xử lý keyboard input.
        """
        
        # ESC vẫn được phép thoát trong lúc chuyển màn.
        if key == pygame.K_ESCAPE:
            self.running = False
            return

        # Không nhận input gameplay trong lúc chuyển level.
        if self.is_level_transition_active():
            return

        # R để restart.
        if key == pygame.K_r:
            self.restart_level()
            return

        # N để sang level tiếp theo.
        if key == pygame.K_n:
            self.next_level()
            return

        # P để quay về level trước.
        if key == pygame.K_p:
            self.previous_level()
            return

        # Mapping phím sang Direction.
        key_to_direction = {
            pygame.K_w: Direction.UP,
            pygame.K_UP: Direction.UP,
            pygame.K_s: Direction.DOWN,
            pygame.K_DOWN: Direction.DOWN,
            pygame.K_a: Direction.LEFT,
            pygame.K_LEFT: Direction.LEFT,
            pygame.K_d: Direction.RIGHT,
            pygame.K_RIGHT: Direction.RIGHT,
        }

        # Nếu phím là phím di chuyển thì move.
        if key in key_to_direction:
            # Nếu phím này đang được giữ, bỏ qua để tránh auto move.
            if key in self.held_move_keys:
                return

            # Đánh dấu phím đang được giữ.
            self.held_move_keys.add(key)

            # Thực hiện đúng 1 move cho lần nhấn này.
            self.move_block(key_to_direction[key])

    def handle_mouse_click(self, mouse_pos: tuple[int, int]) -> None:
        """
        Xử lý click chuột vào button.
        """
        if self.is_level_transition_active():
            return
    
        for button in self.buttons:
            if button.is_clicked(mouse_pos):
                self.handle_button_action(button.action)
                return

    def handle_button_action(self, action: str) -> None:
        """
        Xử lý action từ button.
        """

        if action == "restart":
            self.restart_level()
            return

        if action == "prev_level":
            self.previous_level()
            return

        if action == "next_level":
            self.next_level()
            return

        if action == "quit":
            self.running = False
            return

        if action == "solve_bfs":
            self.handle_solver_button("BFS")
            return

        if action == "solve_dfs":
            self.handle_solver_button("DFS")
            return

        if action == "solve_ucs":
            self.handle_solver_button("UCS")
            return

        if action == "solve_astar":
            self.handle_solver_button("A*")
            return

    def move_block(self, direction: Direction) -> None:
        """
        Di chuyển block.

        Nếu đang animation:
            đưa direction vào input_queue.

        Nếu không animation:
            thực hiện move ngay.
        """
        if self.is_level_transition_active():
            return
        
        if self.is_fall_effect_active():
            return
        
        if self.is_solver_playback:
            self.message = "Solver playback is running."
            self.message_type = "info"
            return

        if self.game.is_goal_state():
            self.message = "You already won. Press R to restart."
            self.message_type = "success"
            return

        # Nếu animation đang chạy, lưu input lại để xử lý sau.
        if self.is_animating:
            # Giới hạn queue để tránh giữ phím quá lâu làm game tự chạy quá nhiều.
            if len(self.input_queue) < 2:
                self.input_queue.append(direction)

            return

        self.perform_move_with_animation(direction)

    def clear_animation_and_input_queue(self) -> None:
        """
        Xóa animation move và input còn chờ.

        Không xóa fall_phase ở đây vì fall effect có hàm riêng quản lý.
        """

        self.input_queue.clear()
        self.held_move_keys.clear()
        self.is_animating = False
        self.animation_from = None
        self.animation_to = None
        self.display_state = None

    def restart_level(self) -> None:
        """
        Restart level hiện tại.
        """
        self.cancel_auto_level_advance()
        self.clear_solver_playback()
        self.clear_animation_and_input_queue()

        self.game.reset()
        self.message = "Level restarted."
        self.message_type = "info"

    def previous_level(self) -> None:
        """
        Chuyển về level trước bằng hiệu ứng fade.
        """

        if self.is_level_transition_active():
            return

        self.cancel_auto_level_advance()

        if self.current_level_index == 0:
            self.message = "Already at the first level."
            self.message_type = "error"
            return

        target_index = self.current_level_index - 1

        self.start_level_transition(target_index)

    def next_level(self) -> None:
        """
        Chuyển sang level tiếp theo bằng hiệu ứng fade.
        """

        if self.is_level_transition_active():
            return

        self.cancel_auto_level_advance()

        if self.current_level_index >= len(self.level_paths) - 1:
            self.message = "Already at the last level."
            self.message_type = "error"
            return

        target_index = self.current_level_index + 1

        self.start_level_transition(target_index)

    def handle_solver_button(self, algorithm: str) -> None:
        """
        Chạy solver được chọn, sau đó tự động animate solution.

        Hiện tại solver giải từ initial state của level,
        vì vậy trước khi playback ta reset game.
        """
                
        if self.is_fall_effect_active():
            return
        
        if self.game.is_goal_state():
            self.message = "Level already completed."
            self.message_type = "success"
            return

        if self.is_animating or self.is_solver_playback:
            self.message = "Please wait for the current animation."
            self.message_type = "error"
            return

        solver_map = {
            "BFS": solve_bfs,
            "DFS": solve_dfs,
            "UCS": solve_ucs,
            "A*": solve_astar,
        }

        solver_function = solver_map.get(algorithm)

        if solver_function is None:
            self.message = f"Unknown solver: {algorithm}"
            self.message_type = "error"
            return

        # Xóa input thủ công còn chờ.
        self.clear_animation_and_input_queue()
        self.clear_solver_playback()

        self.message = f"Running {algorithm}..."
        self.message_type = "info"

        # Vẽ thông báo trước khi bắt đầu tìm.
        self.draw()

        # Solver không làm thay đổi self.game.state.
        result = solver_function(self.game)
        self.last_solver_result = result

        # In metrics ra terminal để dễ debug và dùng cho experiments.
        print()
        print(f"Algorithm       : {result.algorithm}")
        print(f"Success         : {result.success}")
        print(f"Solution length : {result.solution_length}")
        print(f"Expanded nodes  : {result.expanded_nodes}")
        print(f"Search time     : {result.search_time:.6f} seconds")
        print(f"Peak memory     : {result.memory_usage / 1024:.2f} KB")
        print(
            "Solution        :",
            [action.value for action in result.solution],
        )

        if not result.success:
            self.message = result.message
            self.message_type = "error"
            return

        # Solver đã tìm lời giải từ game.state hiện tại,
        # vì vậy playback cũng phải bắt đầu từ đúng vị trí hiện tại.
        self.solver_action_queue = list(result.solution)
        self.is_solver_playback = True

        self.message = (
            f"{algorithm}: {result.solution_length} remaining moves, "
            f"{result.expanded_nodes} nodes"
        )
        self.message_type = "success"
        
    def clear_solver_playback(self) -> None:
        """
        Hủy solution đang được phát.
        """

        self.solver_action_queue.clear()
        self.is_solver_playback = False
        
    def process_solver_playback(self) -> None:
        """
        Mỗi khi animation hiện tại kết thúc,
        lấy action tiếp theo trong solution để chạy.
        """

        if not self.is_solver_playback:
            return

        if self.is_animating:
            return

        if self.is_fall_effect_active():
            return

        # Hết action nghĩa là playback hoàn tất.
        if not self.solver_action_queue:
            self.is_solver_playback = False

            if self.last_solver_result is not None:
                result = self.last_solver_result

                self.message = (
                    f"{result.algorithm} solved: "
                    f"{result.solution_length} moves, "
                    f"{result.search_time:.4f}s"
                )
                self.message_type = "success"

            return

        direction = self.solver_action_queue.pop(0)

        self.perform_move_with_animation(direction)
        
    

    def draw(self) -> None:
        """
        Vẽ lại toàn bộ màn hình.
        """

        self.renderer.draw_background(self.screen)

        # Khi block đang rơi, vẽ block ở falling_block_state.
        if self.fall_phase == "block" and self.falling_block_state is not None:
            board_display_state = self.falling_block_state
            block_y_offset = self.block_fall_y_offset
            tile_offsets = {}
            show_block = True

        # Khi tile đang rơi, block đã rơi mất rồi nên không vẽ block nữa.
        elif self.fall_phase == "tiles":
            board_display_state = self.game.state
            block_y_offset = 0
            tile_offsets = self.tile_fall_offsets
            show_block = False

        # Bình thường.
        else:
            board_display_state = self.display_state
            block_y_offset = 0
            tile_offsets = {}
            show_block = True

        self.renderer.draw_board(
            surface=self.screen,
            board=self.game.board,
            state=self.game.state,
            display_state=board_display_state,
            block_y_offset=block_y_offset,
            tile_fall_offsets=tile_offsets,
            show_block=show_block,
        )

        self.renderer.draw_side_panel(
            surface=self.screen,
            board=self.game.board,
            state=self.game.state,
            move_count=self.game.move_count,
            message=self.message,
            message_type=self.message_type,
            buttons=self.buttons,
        )
        
        # Vẽ transition overlay lên trên toàn bộ board và side panel.
        if self.is_level_transition_active():
            self.renderer.draw_level_transition(
                surface=self.screen,
                alpha=self.level_transition_alpha,
                title=self.transition_title,
                subtitle=self.transition_subtitle,
            )

        pygame.display.flip()
        
    def perform_move_with_animation(self, direction: Direction) -> None:
        """
        Thực hiện move và khởi động animation nếu move hợp lệ.
        """

        old_state = self.game.state

        result = self.game.move(direction)

        if not result.valid:
            self.start_fall_sequence(direction)
            return

        new_state = self.game.state

        self.animation_from = old_state
        self.animation_to = new_state
        self.display_state = old_state
        self.animation_start_time = pygame.time.get_ticks()
        self.is_animating = True

        if result.won:
            self.message = (
                f"You win in {self.game.move_count} moves! "
                f"Next level starts shortly..."
            )
            self.message_type = "success"

            # Hẹn tự động chuyển level sau khi animation hoàn tất.
            self.schedule_auto_level_advance()
        else:
            self.message = result.message
            self.message_type = "info"
            
    def interpolate_state(
        self,
        from_state: BlockState,
        to_state: BlockState,
        t: float,
    ) -> BlockState:
        """
        Nội suy state để vẽ animation.

        Lưu ý:
        - Core state thật vẫn là integer.
        - display_state chỉ dùng để vẽ, nên r/c có thể là float.
        - orientation lấy theo to_state ở nửa sau animation để nhìn tự nhiên hơn.
        """

        r = from_state.r + (to_state.r - from_state.r) * t
        c = from_state.c + (to_state.c - from_state.c) * t

        if t < 0.5:
            orientation = from_state.orientation
        else:
            orientation = to_state.orientation

        return BlockState(r, c, orientation)
    
    def update_animation(self) -> None:
        """
        Cập nhật animation mỗi frame.
        """

        if not self.is_animating:
            self.display_state = None
            return

        if self.animation_from is None or self.animation_to is None:
            self.is_animating = False
            self.display_state = None
            return

        now = pygame.time.get_ticks()

        elapsed_seconds = (now - self.animation_start_time) / 1000.0

        t = elapsed_seconds / theme.MOVE_ANIMATION_DURATION

        if t >= 1.0:
            self.is_animating = False
            self.display_state = None
            self.animation_from = None
            self.animation_to = None
            return

        # Smoothstep giúp chuyển động mềm hơn linear.
        smooth_t = t * t * (3 - 2 * t)

        self.display_state = self.interpolate_state(
            self.animation_from,
            self.animation_to,
            smooth_t,
        )
        
    def process_queued_input_if_possible(self) -> None:
        """
        Nếu không còn animation và queue có input,
        lấy input đầu tiên ra xử lý.
        """

        if self.is_animating:
            return

        if not self.input_queue:
            return

        direction = self.input_queue.pop(0)

        self.perform_move_with_animation(direction)


def run_app() -> None:
    """
    Entry point để main.py gọi.
    """

    app = BloxorzPygameApp()
    app.run()