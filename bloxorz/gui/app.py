from __future__ import annotations

from pathlib import Path

from bloxorz.core.state import BlockState

from bloxorz.core.movement import compute_next_state

import pygame

from bloxorz.core.enums import Direction
from bloxorz.core.game import BloxorzCoreGame
from bloxorz.solvers.base import solver_not_implemented

from . import theme
from .buttons import Button
from .renderer import Renderer


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

            if not self.is_fall_effect_active():
                self.process_queued_input_if_possible()

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

        # ESC để thoát.
        if key == pygame.K_ESCAPE:
            self.running = False
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
        
        if self.is_fall_effect_active():
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
        
        self.clear_animation_and_input_queue()

        self.game.reset()
        self.message = "Level restarted."
        self.message_type = "info"

    def previous_level(self) -> None:
        """
        Chuyển về level trước.
        """
        
        self.clear_animation_and_input_queue()

        if self.current_level_index == 0:
            self.message = "Already at the first level."
            self.message_type = "error"
            return

        self.current_level_index -= 1
        self.game = self.create_game(self.current_level_index)
        self.message = f"Loaded level {self.game.board.id}."
        self.message_type = "info"

    def next_level(self) -> None:
        """
        Chuyển sang level tiếp theo.
        """
        
        self.clear_animation_and_input_queue()

        if self.current_level_index >= len(self.level_paths) - 1:
            self.message = "Already at the last level."
            self.message_type = "error"
            return

        self.current_level_index += 1
        self.game = self.create_game(self.current_level_index)
        self.message = f"Loaded level {self.game.board.id}."
        self.message_type = "info"

    def handle_solver_button(self, algorithm: str) -> None:
        """
        Stub cho solver button.

        Sau này khi có solve_bfs, solve_dfs, solve_ucs, solve_astar,
        ta sẽ thay phần này bằng lời gọi thuật toán thật.
        """

        result = solver_not_implemented(algorithm)

        self.message = result.message
        self.message_type = "error"

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
            self.message = f"You win in {self.game.move_count} moves!"
            self.message_type = "success"
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