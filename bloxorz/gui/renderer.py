from __future__ import annotations

import pygame

from bloxorz.core.board import Board
from bloxorz.core.enums import Orientation
from bloxorz.core.state import BlockState

from . import theme
from .buttons import Button


class Renderer:
    """
    Renderer vẽ giao diện pseudo-3D dạng isometric.

    Core game vẫn là lưới 2D.
    Renderer chỉ biến tọa độ (r, c) thành tọa độ isometric để nhìn giống 3D.
    """

    def __init__(self) -> None:
        # Font lớn dùng cho title.
        self.title_font = pygame.font.SysFont("arial", 28, bold=True)

        # Font vừa dùng cho tiêu đề nhỏ.
        self.medium_font = pygame.font.SysFont("arial", 20, bold=True)

        # Font thường dùng cho text.
        self.normal_font = pygame.font.SysFont("arial", 17)

        # Font nhỏ dùng cho hint.
        self.small_font = pygame.font.SysFont("arial", 14)
        
        # Font lớn dùng cho hiệu ứng chuyển level.
        self.transition_title_font = pygame.font.SysFont(
            "arial",
            46,
            bold=True,
        )

        # Font nhỏ hơn dùng để hiển thị tên level.
        self.transition_subtitle_font = pygame.font.SysFont(
            "arial",
            24,
            bold=False,
        )
        
    def draw_level_transition(
        self,
        surface: pygame.Surface,
        alpha: int,
        title: str,
        subtitle: str,
    ) -> None:
        """
        Vẽ lớp phủ chuyển level.

        alpha:
            0   = hoàn toàn trong suốt.
            255 = hoàn toàn tối.

        title:
            Ví dụ: "LEVEL COMPLETE" hoặc "LEVEL 2".

        subtitle:
            Tên level hiện tại hoặc level tiếp theo.
        """

        # Không cần vẽ khi hoàn toàn trong suốt.
        if alpha <= 0:
            return

        alpha = max(0, min(255, alpha))

        # Tạo surface trong suốt bằng kích thước cửa sổ.
        overlay = pygame.Surface(
            surface.get_size(),
            pygame.SRCALPHA,
        )

        # Tô màu tối với alpha hiện tại.
        overlay.fill(
            (
                *theme.LEVEL_TRANSITION_OVERLAY_COLOR,
                alpha,
            )
        )

        # Đè overlay lên toàn màn hình.
        surface.blit(overlay, (0, 0))

        # Chỉ hiện chữ khi màn hình đã tối tương đối.
        text_alpha = int(
            max(
                0,
                min(
                    255,
                    (alpha - 70) / 185 * 255,
                ),
            )
        )

        if text_alpha <= 0:
            return

        # Render tiêu đề.
        title_surface = self.transition_title_font.render(
            title,
            True,
            theme.LEVEL_TRANSITION_TITLE_COLOR,
        )

        title_surface.set_alpha(text_alpha)

        title_rect = title_surface.get_rect(
            center=(
                theme.WINDOW_WIDTH // 2,
                theme.WINDOW_HEIGHT // 2 - 28,
            )
        )

        surface.blit(title_surface, title_rect)

        # Render tên level.
        subtitle_surface = self.transition_subtitle_font.render(
            subtitle,
            True,
            theme.LEVEL_TRANSITION_SUBTITLE_COLOR,
        )

        subtitle_surface.set_alpha(text_alpha)

        subtitle_rect = subtitle_surface.get_rect(
            center=(
                theme.WINDOW_WIDTH // 2,
                theme.WINDOW_HEIGHT // 2 + 32,
            )
        )

        surface.blit(subtitle_surface, subtitle_rect)
        
    def draw_background(self, surface: pygame.Surface) -> None:
        """
        Vẽ nền đỏ cam kiểu Bloxorz gốc.

        Ta dùng gradient nhiều dòng ngang để tạo cảm giác có chiều sâu.
        """

        width = surface.get_width()
        height = surface.get_height()

        for y in range(height):
            # t chạy từ 0 ở trên xuống 1 ở dưới.
            t = y / max(1, height - 1)

            if t < 0.55:
                # Nội suy từ top sang mid.
                local_t = t / 0.55
                start = theme.COLOR_BACKGROUND_TOP
                end = theme.COLOR_BACKGROUND_MID
            else:
                # Nội suy từ mid sang bottom.
                local_t = (t - 0.55) / 0.45
                start = theme.COLOR_BACKGROUND_MID
                end = theme.COLOR_BACKGROUND_BOTTOM

            r = int(start[0] + (end[0] - start[0]) * local_t)
            g = int(start[1] + (end[1] - start[1]) * local_t)
            b = int(start[2] + (end[2] - start[2]) * local_t)

            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

        # Thêm vài bóng tối mềm phía dưới để nền bớt phẳng.
        shadow_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        pygame.draw.ellipse(
            shadow_surface,
            theme.COLOR_SHADOW,
            pygame.Rect(-120, height - 210, width // 2, 120),
        )

        pygame.draw.ellipse(
            shadow_surface,
            (0, 0, 0, 65),
            pygame.Rect(width // 4, height - 170, width // 2, 90),
        )

        surface.blit(shadow_surface, (0, 0))
        
    def draw_board_shadow(
        self,
        surface: pygame.Surface,
        board: Board,
        origin_x: int,
        origin_y: int,
    ) -> None:
        """
        Vẽ bóng mềm dưới toàn bộ board để board nổi khỏi nền.
        """

        shadow_surface = pygame.Surface(
            (theme.WINDOW_WIDTH, theme.WINDOW_HEIGHT),
            pygame.SRCALPHA,
        )

        # Tính tâm board theo isometric tương đối.
        center_r = board.rows / 2
        center_c = board.cols / 2
        center_x, center_y = self.grid_to_iso(center_r, center_c, origin_x, origin_y)

        shadow_rect = pygame.Rect(
            center_x - 360,
            center_y + 80,
            720,
            120,
        )

        pygame.draw.ellipse(
            shadow_surface,
            (0, 0, 0, 85),
            shadow_rect,
        )

        surface.blit(shadow_surface, (0, 0))
        
    def draw_tile_surface_details(
        self,
        surface: pygame.Surface,
        r: int,
        c: int,
        top: tuple[int, int],
        right: tuple[int, int],
        bottom: tuple[int, int],
        left: tuple[int, int],
    ) -> None:
        """
        Vẽ vài vệt sáng/nứt nhỏ trên mặt tile.

        Dùng công thức theo r,c để tạo pattern cố định,
        không bị random thay đổi mỗi frame.
        """

        seed = (r * 37 + c * 17) % 100

        # Một vệt sáng nhẹ.
        if seed % 3 == 0:
            p1 = (
                int((top[0] * 0.55 + left[0] * 0.45)),
                int((top[1] * 0.55 + left[1] * 0.45)),
            )
            p2 = (
                int((right[0] * 0.55 + bottom[0] * 0.45)),
                int((right[1] * 0.55 + bottom[1] * 0.45)),
            )

            pygame.draw.line(surface, (215, 220, 220), p1, p2, width=1)

        # Một vệt nứt nhỏ tối.
        if seed % 4 == 0:
            center_x = (top[0] + right[0] + bottom[0] + left[0]) // 4
            center_y = (top[1] + right[1] + bottom[1] + left[1]) // 4

            pygame.draw.line(
                surface,
                (115, 122, 125),
                (center_x - 8, center_y - 2),
                (center_x + 7, center_y + 3),
                width=1,
            )
            
    def draw_block_texture(
        self,
        surface: pygame.Surface,
        r: float,
        c: float,
        top2: tuple[int, int],
        right2: tuple[int, int],
        bottom2: tuple[int, int],
        left2: tuple[int, int],
        left: tuple[int, int],
        right: tuple[int, int],
        bottom: tuple[int, int],
    ) -> None:
        """
        Vẽ texture đơn giản lên block:
        - vài vệt gỉ sáng
        - vài mảng tối
        - vài đường dọc như khối đá/kim loại cũ
        """

        seed = int((r * 41 + c * 29) % 100)

        # Vệt sáng trên mặt trên.
        pygame.draw.line(
            surface,
            theme.COLOR_BLOCK_HIGHLIGHT,
            (
                int((top2[0] * 0.7 + left2[0] * 0.3)),
                int((top2[1] * 0.7 + left2[1] * 0.3)),
            ),
            (
                int((right2[0] * 0.65 + bottom2[0] * 0.35)),
                int((right2[1] * 0.65 + bottom2[1] * 0.35)),
            ),
            width=2,
        )

        # Mảng tối nhỏ trên mặt trái.
        stain_center = (
            int((left2[0] + bottom2[0] + bottom[0] + left[0]) / 4),
            int((left2[1] + bottom2[1] + bottom[1] + left[1]) / 4),
        )

        pygame.draw.ellipse(
            surface,
            theme.COLOR_BLOCK_DARK_STAIN,
            pygame.Rect(stain_center[0] - 8, stain_center[1] - 10, 16, 22),
        )

        # Đường dọc mặt phải.
        pygame.draw.line(
            surface,
            (145, 82, 50),
            (
                int((right2[0] * 0.6 + bottom2[0] * 0.4)),
                int((right2[1] * 0.6 + bottom2[1] * 0.4)),
            ),
            (
                int((right[0] * 0.6 + bottom[0] * 0.4)),
                int((right[1] * 0.6 + bottom[1] * 0.4)),
            ),
            width=2,
        )

        # Một vài vệt phụ thay đổi theo vị trí.
        if seed % 2 == 0:
            pygame.draw.line(
                surface,
                (95, 55, 42),
                (
                    int((left2[0] + bottom2[0]) / 2),
                    int((left2[1] + bottom2[1]) / 2),
                ),
                (
                    int((left[0] + bottom[0]) / 2),
                    int((left[1] + bottom[1]) / 2),
                ),
                width=2,
            )

    def compute_origin(self, board: Board) -> tuple[int, int]:
        """
        Tính gốc vẽ board isometric.

        Với isometric:
        x = origin_x + (c - r) * tile_width / 2
        y = origin_y + (c + r) * tile_height / 2

        Ta căn board vào vùng bên trái, chừa panel bên phải.
        """

        board_area_width = theme.WINDOW_WIDTH - theme.SIDE_PANEL_WIDTH

        # Ước lượng kích thước board sau khi chiếu isometric.
        iso_width = (board.rows + board.cols) * theme.ISO_TILE_WIDTH // 2
        iso_height = (board.rows + board.cols) * theme.ISO_TILE_HEIGHT // 2

        # Căn giữa theo chiều ngang.
        origin_x = (board_area_width - iso_width) // 2 + board.rows * theme.ISO_TILE_WIDTH // 2

        # Căn giữa theo chiều dọc, hơi đẩy lên để block đứng không chạm đáy.
        origin_y = (theme.WINDOW_HEIGHT - iso_height) // 2 + 80

        return origin_x, origin_y

    def grid_to_iso(
        self,
        r: float,
        c: float,
        origin_x: int,
        origin_y: int,
    ) -> tuple[int, int]:
        """
        Đổi tọa độ grid (r, c) sang tọa độ isometric trên màn hình.
        """

        x = origin_x + (c - r) * theme.ISO_TILE_WIDTH / 2
        y = origin_y + (c + r) * theme.ISO_TILE_HEIGHT / 2

        return int(x), int(y)

    def get_tile_points(
        self,
        x: int,
        y: int,
    ) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]:
        """
        Trả về 4 đỉnh của mặt trên tile dạng hình thoi.
        """

        half_w = theme.ISO_TILE_WIDTH // 2
        half_h = theme.ISO_TILE_HEIGHT // 2

        top = (x, y)
        right = (x + half_w, y + half_h)
        bottom = (x, y + theme.ISO_TILE_HEIGHT)
        left = (x - half_w, y + half_h)

        return top, right, bottom, left

    def get_tile_colors(
        self,
        cell: str,
    ) -> tuple[
        tuple[int, int, int],
        tuple[int, int, int],
        tuple[int, int, int],
    ]:
        """
        Trả về ba màu của một tile pseudo-3D:

        - màu mặt trên;
        - màu mặt trái;
        - màu mặt phải.

        Bridge không được xử lý màu trong hàm này nữa,
        vì bridge sẽ được vẽ bằng draw_open_bridge()
        hoặc draw_closed_bridge() trong draw_tile().
        """

        # Goal vẫn sử dụng màu xanh lá riêng.
        if cell == Board.GOAL:
            return (
                theme.COLOR_GOAL_TOP,
                theme.COLOR_GOAL_LEFT,
                theme.COLOR_GOAL_RIGHT,
            )

        # Start vẫn sử dụng màu xanh dương riêng.
        if cell == Board.START:
            return (
                theme.COLOR_START_TOP,
                theme.COLOR_START_LEFT,
                theme.COLOR_START_RIGHT,
            )

        # Fragile tile có màu cam riêng.
        # Sau khi mặt tile được vẽ, draw_fragile_overlay()
        # sẽ vẽ thêm các đường nứt lên trên.
        if cell == "F":
            return (
                theme.COLOR_FRAGILE_TOP,
                theme.COLOR_FRAGILE_LEFT,
                theme.COLOR_FRAGILE_RIGHT,
            )

        # Các switch dùng nền gạch bình thường.
        # Hình dạng nút tròn, chữ X hoặc ngoặc sẽ được
        # vẽ đè lên sau bằng các hàm overlay.
        if cell in ("X", "O", "P"):
            return (
                theme.COLOR_TILE_TOP,
                theme.COLOR_TILE_LEFT,
                theme.COLOR_TILE_RIGHT,
            )

        # Floor và các tile thông thường.
        return (
            theme.COLOR_TILE_TOP,
            theme.COLOR_TILE_LEFT,
            theme.COLOR_TILE_RIGHT,
        )

    def draw_board(
        self,
        surface: pygame.Surface,
        board: Board,
        state: BlockState,
        display_state: BlockState | None = None,
        block_y_offset: int = 0,
        tile_fall_offsets: dict[tuple[int, int], int] | None = None,
        show_block: bool = True,
        bridge_progress: dict[tuple[int, int], float] | None = None,
        hidden_tiles: set[tuple[int, int]] | None = None,
    ) -> None:
        """
        Vẽ board và block.

        display_state:
            State dùng để vẽ animation di chuyển.

        block_y_offset:
            Offset theo trục y màn hình cho block.
            Dùng khi block rơi xuống khỏi map.

        tile_fall_offsets:
            Dict {(r, c): y_offset}.
            Dùng khi từng tile rơi xuống.

        show_block:
            False khi block đã rơi mất khỏi màn hình.
        """
        if tile_fall_offsets is None:
            tile_fall_offsets = {}
            
        if hidden_tiles is None:
            hidden_tiles = set()
    
        origin_x, origin_y = self.compute_origin(board)
        self.draw_board_shadow(surface, board, origin_x, origin_y)

        if tile_fall_offsets is None:
            tile_fall_offsets = {}

        # Vẽ tile theo thứ tự r+c tăng dần để giữ cảm giác isometric.
        for r in range(board.rows):
            for c in range(board.cols):
                # Fragile đã vỡ thì bỏ qua tile này.
                if (r, c) in hidden_tiles:
                    continue
                
                cell = board.cell_at(r, c)

                if cell == Board.VOID:
                    continue

                y_offset = tile_fall_offsets.get((r, c), 0)

                self.draw_tile(
                    surface=surface,
                    board=board,
                    r=r,
                    c=c,
                    origin_x=origin_x,
                    origin_y=origin_y,
                    screen_y_offset=y_offset,
                    bridge_progress=bridge_progress,
                )

        # Goal marker cũng phải rơi theo tile goal.
        goal_offset = tile_fall_offsets.get(board.goal, 0)

        self.draw_goal_marker(
            surface=surface,
            board=board,
            origin_x=origin_x,
            origin_y=origin_y,
            screen_y_offset=goal_offset,
        )

        if show_block:
            block_state = display_state if display_state is not None else state

            self.draw_block(
                surface=surface,
                state=block_state,
                origin_x=origin_x,
                origin_y=origin_y,
                screen_y_offset=block_y_offset,
            )

    def draw_tile(
        self,
        surface: pygame.Surface,
        board: Board,
        r: int,
        c: int,
        origin_x: int,
        origin_y: int,
        screen_y_offset: int = 0,

        # Progress hình ảnh của từng bridge.
        # 0.0 = đóng hoàn toàn.
        # 1.0 = mở hoàn toàn.
        bridge_progress: dict[tuple[int, int], float] | None = None,
    ) -> None:
        """
        Vẽ một tile pseudo-3D.

        Các tile thông thường:
        - floor
        - start
        - goal
        - fragile
        - soft switch
        - heavy switch

        Bridge được xử lý riêng bằng:
        - draw_closed_bridge()
        - draw_open_bridge()
        """

        # Đọc ký hiệu tile thật trong grid JSON.
        cell = board.cell_at(r, c)

        # Chuyển tọa độ hàng/cột sang tọa độ isometric trên màn hình.
        x, y = self.grid_to_iso(
            r,
            c,
            origin_x,
            origin_y,
        )

        # Khi map đang có hiệu ứng rơi,
        # tile được dịch xuống theo screen_y_offset.
        y += screen_y_offset

        # Bridge được vẽ bằng model riêng,
        # không vẽ giống tile đá thông thường.
        if cell == "B":
            # Nếu app chưa truyền animation progress,
            # renderer vẽ ngay theo trạng thái logic thật.
            if bridge_progress is None:
                visual_progress = (
                    1.0
                    if self.is_bridge_open(board, r, c)
                    else 0.0
                )

            # Nếu app đã truyền progress,
            # lấy tiến độ mở/đóng hiện tại của đúng ô bridge này.
            else:
                visual_progress = bridge_progress.get(
                    (r, c),
                    0.0,
                )

            # Cầu đóng hoàn toàn:
            # chỉ vẽ dấu neo nhỏ.
            if visual_progress <= 0.001:
                self.draw_closed_bridge(
                    surface=surface,
                    x=x,
                    y=y,
                )

            # Cầu đang mở hoặc đã mở:
            # progress quyết định độ dài cầu được kéo ra.
            else:
                self.draw_open_bridge(
                    surface=surface,
                    x=x,
                    y=y,
                    progress=visual_progress,
                )

            # Bridge đã được vẽ riêng nên không chạy xuống
            # phần vẽ tile thông thường bên dưới.
            return

        # ========================================================
        # TILE THÔNG THƯỜNG
        # ========================================================

        # Lấy ba màu:
        # - mặt trên
        # - mặt trái
        # - mặt phải
        top_color, left_color, right_color = (
            self.get_tile_colors(cell)
        )

        # Lấy bốn đỉnh của mặt trên hình thoi.
        top, right, bottom, left = self.get_tile_points(
            x,
            y,
        )

        # Độ dày của tile.
        depth = theme.ISO_TILE_DEPTH

        # Các điểm được dịch xuống để tạo mặt bên tile.
        bottom_down = (
            bottom[0],
            bottom[1] + depth,
        )

        left_down = (
            left[0],
            left[1] + depth,
        )

        right_down = (
            right[0],
            right[1] + depth,
        )

        # ========================================================
        # VẼ HÌNH KHỐI TILE
        # ========================================================

        # Mặt trái.
        pygame.draw.polygon(
            surface,
            left_color,
            [
                left,
                bottom,
                bottom_down,
                left_down,
            ],
        )

        # Mặt phải.
        pygame.draw.polygon(
            surface,
            right_color,
            [
                right,
                bottom,
                bottom_down,
                right_down,
            ],
        )

        # Mặt trên.
        pygame.draw.polygon(
            surface,
            top_color,
            [
                top,
                right,
                bottom,
                left,
            ],
        )

        # Viền mặt trên.
        pygame.draw.polygon(
            surface,
            theme.COLOR_GRID_LINE,
            [
                top,
                right,
                bottom,
                left,
            ],
            width=1,
        )

        # Vẽ texture sau mặt trên.
        # Nếu đặt trước mặt trên, texture sẽ bị polygon đè mất.
        self.draw_tile_surface_details(
            surface=surface,
            r=r,
            c=c,
            top=top,
            right=right,
            bottom=bottom,
            left=left,
        )

        # ========================================================
        # VẼ HÌNH DẠNG CỦA ADVANCED TILE
        # ========================================================

        if cell == "F":
            # Fragile: vẽ các đường nứt.
            self.draw_fragile_overlay(
                surface=surface,
                top=top,
                right=right,
                bottom=bottom,
                left=left,
            )

        elif cell == "X":
            # Soft switch: vẽ nút tròn nổi.
            self.draw_soft_switch_overlay(
                surface=surface,
                top=top,
                right=right,
                bottom=bottom,
                left=left,
            )

        elif cell == "O":
            # Heavy switch: vẽ tấm chữ X.
            self.draw_heavy_switch_overlay(
                surface=surface,
                top=top,
                right=right,
                bottom=bottom,
                left=left,
            )

        # Sau này, khi đã tạo draw_split_switch_overlay(),
        # bạn có thể mở phần này:
        #
        # elif cell == "P":
        #     self.draw_split_switch_overlay(
        #         surface=surface,
        #         top=top,
        #         right=right,
        #         bottom=bottom,
        #         left=left,
        #     )

        # ========================================================
        # CHỈ HIỂN THỊ CHỮ CHO START VÀ GOAL
        # ========================================================

        if cell in (
            Board.START,
            Board.GOAL,
        ):
            label_surface = self.small_font.render(
                cell,
                True,
                theme.COLOR_TEXT,
            )

            label_rect = label_surface.get_rect(
                center=(
                    x,
                    y + theme.ISO_TILE_HEIGHT // 2,
                )
            )

            surface.blit(
                label_surface,
                label_rect,
            )

    def draw_goal_marker(
        self,
        surface: pygame.Surface,
        board: Board,
        origin_x: int,
        origin_y: int,
        screen_y_offset: int = 0,
    ) -> None:
        """
        Vẽ lỗ goal như một hình thoi tối ở trên tile goal.

        screen_y_offset giúp goal marker rơi theo tile goal.
        """

        r, c = board.goal

        x, y = self.grid_to_iso(r, c, origin_x, origin_y)

        y += screen_y_offset

        top, right, bottom, left = self.get_tile_points(x, y)

        center_x = x
        center_y = y + theme.ISO_TILE_HEIGHT // 2

        small_points = []

        for px, py in [top, right, bottom, left]:
            sx = center_x + int((px - center_x) * 0.46)
            sy = center_y + int((py - center_y) * 0.46)
            small_points.append((sx, sy))

        pygame.draw.polygon(
            surface,
            (35, 32, 28),
            small_points,
        )

        pygame.draw.polygon(
            surface,
            (10, 10, 10),
            small_points,
            width=2,
        )
        
    def draw_fragile_shatter(
        self,
        surface: pygame.Surface,
        board: Board,
        cell: tuple[int, int],
        progress: float,
    ) -> None:
        """
        Vẽ tile fragile thành nhiều mảnh nhỏ đang rơi.
        """

        progress = max(
            0.0,
            min(1.0, progress),
        )

        origin_x, origin_y = self.compute_origin(
            board
        )

        r, c = cell

        x, y = self.grid_to_iso(
            r,
            c,
            origin_x,
            origin_y,
        )

        top, right, bottom, left = (
            self.get_tile_points(x, y)
        )

        center = (
            (
                top[0]
                + right[0]
                + bottom[0]
                + left[0]
            ) // 4,
            (
                top[1]
                + right[1]
                + bottom[1]
                + left[1]
            ) // 4,
        )

        edge_points = [
            top,
            self.lerp_point(top, right, 0.5),
            right,
            self.lerp_point(right, bottom, 0.5),
            bottom,
            self.lerp_point(bottom, left, 0.5),
            left,
            self.lerp_point(left, top, 0.5),
        ]

        velocities = [
            (-42, -30),
            (12, -38),
            (52, -14),
            (65, 12),
            (24, 30),
            (-22, 35),
            (-58, 15),
            (-60, -12),
        ]

        gravity = 250

        for index in range(8):
            point_a = edge_points[index]
            point_b = edge_points[
                (index + 1) % 8
            ]

            velocity_x, velocity_y = velocities[index]

            offset_x = int(
                velocity_x * progress
            )

            offset_y = int(
                velocity_y * progress
                + gravity * progress * progress
            )

            fragment = [
                (
                    center[0] + offset_x,
                    center[1] + offset_y,
                ),
                (
                    point_a[0] + offset_x,
                    point_a[1] + offset_y,
                ),
                (
                    point_b[0] + offset_x,
                    point_b[1] + offset_y,
                ),
            ]

            color = (
                theme.COLOR_FRAGILE_TOP
                if index % 2 == 0
                else theme.COLOR_FRAGILE_RIGHT
            )

            pygame.draw.polygon(
                surface,
                color,
                fragment,
            )

            pygame.draw.polygon(
                surface,
                theme.COLOR_FRAGILE_CRACK,
                fragment,
                width=1,
            )

    def draw_block(
        self,
        surface: pygame.Surface,
        state: BlockState,
        origin_x: int,
        origin_y: int,
        screen_y_offset: int = 0,
    ) -> None:
        """
        Vẽ block pseudo-3D.

        screen_y_offset dùng để block rơi xuống khỏi map.
        """

        if state.orientation == Orientation.STANDING:
            height = theme.BLOCK_STANDING_HEIGHT
            cells = state.occupied_cells()
        else:
            height = theme.BLOCK_LYING_HEIGHT
            cells = state.occupied_cells()

        sorted_cells = sorted(cells, key=lambda cell: cell[0] + cell[1])

        for r, c in sorted_cells:
            self.draw_block_prism(
                surface=surface,
                r=r,
                c=c,
                height=height,
                origin_x=origin_x,
                origin_y=origin_y,
                screen_y_offset=screen_y_offset,
            )

        self.draw_orientation_label(
            surface=surface,
            state=state,
            origin_x=origin_x,
            origin_y=origin_y,
            height=height,
            screen_y_offset=screen_y_offset,
        )
    
    def draw_block_prism(
        self,
        surface: pygame.Surface,
        r: float,
        c: float,
        height: int,
        origin_x: int,
        origin_y: int,
        screen_y_offset: int = 0,
    ) -> None:
        """
        Vẽ một lăng trụ isometric đặt trên tile (r, c).

        screen_y_offset dùng để block rơi xuống dưới màn hình.
        """

        base_x, base_y = self.grid_to_iso(r, c, origin_x, origin_y)

        base_y += screen_y_offset

        top, right, bottom, left = self.get_tile_points(base_x, base_y)

        top2 = (top[0], top[1] - height)
        right2 = (right[0], right[1] - height)
        bottom2 = (bottom[0], bottom[1] - height)
        left2 = (left[0], left[1] - height)

        pygame.draw.polygon(
            surface,
            theme.COLOR_BLOCK_LEFT,
            [left2, bottom2, bottom, left],
        )

        pygame.draw.polygon(
            surface,
            theme.COLOR_BLOCK_RIGHT,
            [right2, bottom2, bottom, right],
        )

        pygame.draw.polygon(
            surface,
            theme.COLOR_BLOCK_TOP,
            [top2, right2, bottom2, left2],
        )

        pygame.draw.polygon(
            surface,
            theme.COLOR_BLOCK_EDGE,
            [top2, right2, bottom2, left2],
            width=2,
        )

        pygame.draw.line(surface, theme.COLOR_BLOCK_EDGE, left2, left, width=2)
        pygame.draw.line(surface, theme.COLOR_BLOCK_EDGE, right2, right, width=2)
        pygame.draw.line(surface, theme.COLOR_BLOCK_EDGE, bottom2, bottom, width=2)
    
    def draw_orientation_label(
        self,
        surface: pygame.Surface,
        state: BlockState,
        origin_x: int,
        origin_y: int,
        height: int,
        screen_y_offset: int = 0,
    ) -> None:
        """
        Vẽ nhãn STAND/HOR/VER trên block.
        """

        if state.orientation == Orientation.STANDING:
            label = "STAND"
        elif state.orientation == Orientation.HORIZONTAL:
            label = "HOR"
        else:
            label = "VER"

        cells = state.occupied_cells()

        avg_r = sum(r for r, _ in cells) / len(cells)
        avg_c = sum(c for _, c in cells) / len(cells)

        x, y = self.grid_to_iso(avg_r, avg_c, origin_x, origin_y)

        y += screen_y_offset

        label_surface = self.small_font.render(
            label,
            True,
            (45, 30, 10),
        )

        label_rect = label_surface.get_rect(
            center=(x, y + theme.ISO_TILE_HEIGHT // 2 - height),
        )

        surface.blit(label_surface, label_rect)

    def draw_side_panel(
        self,
        surface: pygame.Surface,
        board: Board,
        state: BlockState,
        move_count: int,
        message: str,
        message_type: str,
        buttons: list[Button],
    ) -> None:
        """
        Vẽ panel bên phải.
        """

        panel_x = theme.WINDOW_WIDTH - theme.SIDE_PANEL_WIDTH

        panel_rect = pygame.Rect(
            panel_x,
            0,
            theme.SIDE_PANEL_WIDTH,
            theme.WINDOW_HEIGHT,
        )

        pygame.draw.rect(surface, theme.COLOR_PANEL, panel_rect)

        x = panel_x + 20
        y = 26

        self.draw_text(surface, "Bloxorz Solver", x, y, self.title_font)
        y += 48

        self.draw_text(surface, f"Level {board.id}: {board.name}", x, y, self.medium_font)
        y += 28

        self.draw_text(
            surface,
            f"Difficulty: {board.difficulty}",
            x,
            y,
            self.normal_font,
            theme.COLOR_TEXT_MUTED,
        )
        y += 24

        description = board.description
        if len(description) > 34:
            description = description[:34] + "..."

        self.draw_text(
            surface,
            description,
            x,
            y,
            self.small_font,
            theme.COLOR_TEXT_MUTED,
        )
        y += 42

        self.draw_text(surface, "Current State", x, y, self.medium_font)
        y += 28

        self.draw_text(
            surface,
            f"Anchor: ({state.r}, {state.c})",
            x,
            y,
            self.normal_font,
            theme.COLOR_TEXT_MUTED,
        )
        y += 24

        self.draw_text(
            surface,
            f"Orientation: {state.orientation.value}",
            x,
            y,
            self.normal_font,
            theme.COLOR_TEXT_MUTED,
        )
        y += 24

        self.draw_text(
            surface,
            f"Moves: {move_count}",
            x,
            y,
            self.medium_font,
            theme.COLOR_SUCCESS,
        )
        y += 40

        self.draw_text(surface, "Message", x, y, self.medium_font)
        y += 28

        if message_type == "error":
            message_color = theme.COLOR_ERROR
        elif message_type == "success":
            message_color = theme.COLOR_SUCCESS
        else:
            message_color = theme.COLOR_TEXT_MUTED

        self.draw_text(
            surface,
            message,
            x,
            y,
            self.normal_font,
            message_color,
        )
        y += 42

        self.draw_text(surface, "Controls", x, y, self.medium_font)
        y += 24

        controls = [
            "WASD / Arrow keys: Move",
            "R: Restart",
            "N/P: Next/Previous level",
            "H: How to Play",
            "ESC: Quit",
        ]

        for line in controls:
            self.draw_text(
                surface,
                line,
                x,
                y,
                self.small_font,
                theme.COLOR_TEXT_MUTED,
            )
            y += 18

        mouse_pos = pygame.mouse.get_pos()

        for button in buttons:
            button.draw(surface, self.normal_font, mouse_pos)

    def draw_text(
        self,
        surface: pygame.Surface,
        text: str,
        x: int,
        y: int,
        font: pygame.font.Font,
        color: tuple[int, int, int] = theme.COLOR_TEXT,
    ) -> None:
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (x, y))
        
    def lerp_point(
        self,
        point_a: tuple[int, int],
        point_b: tuple[int, int],
        t: float,
    ) -> tuple[int, int]:
        """
        Trả về điểm nằm giữa point_a và point_b.

        t = 0.0: point_a
        t = 0.5: trung điểm
        t = 1.0: point_b
        """

        return (
            int(
                point_a[0]
                + (point_b[0] - point_a[0]) * t
            ),
            int(
                point_a[1]
                + (point_b[1] - point_a[1]) * t
            ),
        )
        
    def inset_diamond(
        self,
        top: tuple[int, int],
        right: tuple[int, int],
        bottom: tuple[int, int],
        left: tuple[int, int],
        scale: float,
    ) -> list[tuple[int, int]]:
        """
        Thu nhỏ mặt hình thoi của tile về phía tâm.

        scale = 1.0: giữ nguyên kích thước.
        scale = 0.5: còn một nửa.
        """

        center_x = (
            top[0] + right[0] + bottom[0] + left[0]
        ) // 4

        center_y = (
            top[1] + right[1] + bottom[1] + left[1]
        ) // 4

        result: list[tuple[int, int]] = []

        for x, y in (top, right, bottom, left):
            result.append(
                (
                    center_x
                    + int((x - center_x) * scale),
                    center_y
                    + int((y - center_y) * scale),
                )
            )

        return result
    
    def is_bridge_open(
        self,
        board: Board,
        r: int,
        c: int,
    ) -> bool:
        """
        Trả về True nếu bridge tại (r, c) đang mở.

        Renderer chỉ đọc trạng thái, không thay đổi logic game.
        """

        rule_extension = getattr(
            board,
            "rule_extension",
            None,
        )

        if rule_extension is None:
            return False

        bridge_states = getattr(
            rule_extension,
            "bridge_states",
            {},
        )

        return bool(
            bridge_states.get((r, c), False)
        )
    
    def draw_fragile_overlay(
        self,
        surface: pygame.Surface,
        top: tuple[int, int],
        right: tuple[int, int],
        bottom: tuple[int, int],
        left: tuple[int, int],
    ) -> None:
        """
        Vẽ các đường nứt đặc trưng của fragile tile.
        """

        center = (
            (
                top[0]
                + right[0]
                + bottom[0]
                + left[0]
            ) // 4,
            (
                top[1]
                + right[1]
                + bottom[1]
                + left[1]
            ) // 4,
        )

        main_cracks = [
            self.lerp_point(top, right, 0.55),
            self.lerp_point(right, bottom, 0.52),
            self.lerp_point(bottom, left, 0.58),
            self.lerp_point(left, top, 0.62),
        ]

        for end_point in main_cracks:
            pygame.draw.line(
                surface,
                theme.COLOR_FRAGILE_CRACK,
                center,
                end_point,
                width=2,
            )

        # Hai nhánh nứt nhỏ để tile trông tự nhiên hơn.
        branch_1 = self.lerp_point(
            center,
            main_cracks[0],
            0.55,
        )

        pygame.draw.line(
            surface,
            theme.COLOR_FRAGILE_CRACK,
            branch_1,
            (
                branch_1[0] - 7,
                branch_1[1] + 3,
            ),
            width=1,
        )

        branch_2 = self.lerp_point(
            center,
            main_cracks[2],
            0.5,
        )

        pygame.draw.line(
            surface,
            theme.COLOR_FRAGILE_CRACK,
            branch_2,
            (
                branch_2[0] + 8,
                branch_2[1] - 3,
            ),
            width=1,
        )
        
    def draw_soft_switch_overlay(
        self,
        surface: pygame.Surface,
        top: tuple[int, int],
        right: tuple[int, int],
        bottom: tuple[int, int],
        left: tuple[int, int],
    ) -> None:
        """
        Vẽ soft switch thành nút áp lực tròn nổi.

        Do mặt board là isometric nên hình tròn được vẽ thành ellipse.
        """

        center_x = (
            top[0] + right[0] + bottom[0] + left[0]
        ) // 4

        center_y = (
            top[1] + right[1] + bottom[1] + left[1]
        ) // 4

        switch_width = int(
            theme.ISO_TILE_WIDTH * 0.46
        )

        switch_height = int(
            theme.ISO_TILE_HEIGHT * 0.48
        )

        # Bóng/mặt bên của nút.
        side_rect = pygame.Rect(
            center_x - switch_width // 2,
            center_y - switch_height // 2 + 4,
            switch_width,
            switch_height,
        )

        pygame.draw.ellipse(
            surface,
            theme.COLOR_SOFT_SWITCH_SIDE,
            side_rect,
        )

        # Mặt trên.
        top_rect = pygame.Rect(
            center_x - switch_width // 2,
            center_y - switch_height // 2,
            switch_width,
            switch_height,
        )

        pygame.draw.ellipse(
            surface,
            theme.COLOR_SOFT_SWITCH_TOP,
            top_rect,
        )

        pygame.draw.ellipse(
            surface,
            theme.COLOR_SOFT_SWITCH_EDGE,
            top_rect,
            width=2,
        )

        # Vệt sáng nhỏ.
        highlight_rect = top_rect.inflate(-9, -7)

        pygame.draw.arc(
            surface,
            theme.COLOR_SOFT_SWITCH_HIGHLIGHT,
            highlight_rect,
            3.3,
            5.7,
            width=2,
        )
        
    def draw_heavy_switch_overlay(
        self,
        surface: pygame.Surface,
        top: tuple[int, int],
        right: tuple[int, int],
        bottom: tuple[int, int],
        left: tuple[int, int],
    ) -> None:
        """
        Vẽ heavy switch thành tấm kim loại hình chữ X.
        """

        inner = self.inset_diamond(
            top,
            right,
            bottom,
            left,
            0.62,
        )

        (
            inner_top,
            inner_right,
            inner_bottom,
            inner_left,
        ) = inner

        # Bóng phía dưới.
        pygame.draw.line(
            surface,
            theme.COLOR_HEAVY_SWITCH_EDGE,
            (
                inner_left[0],
                inner_left[1] + 3,
            ),
            (
                inner_right[0],
                inner_right[1] + 3,
            ),
            width=9,
        )

        pygame.draw.line(
            surface,
            theme.COLOR_HEAVY_SWITCH_EDGE,
            (
                inner_top[0],
                inner_top[1] + 3,
            ),
            (
                inner_bottom[0],
                inner_bottom[1] + 3,
            ),
            width=9,
        )

        # Thân chữ X.
        pygame.draw.line(
            surface,
            theme.COLOR_HEAVY_SWITCH_TOP,
            inner_left,
            inner_right,
            width=7,
        )

        pygame.draw.line(
            surface,
            theme.COLOR_HEAVY_SWITCH_TOP,
            inner_top,
            inner_bottom,
            width=7,
        )

        # Highlight.
        pygame.draw.line(
            surface,
            theme.COLOR_HEAVY_SWITCH_HIGHLIGHT,
            inner_left,
            inner_right,
            width=2,
        )
        
    def draw_closed_bridge(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
    ) -> None:
        """
        Bridge đóng gần như là void hoàn toàn.

        Chỉ vẽ hai bệ neo rất nhỏ ở hai đầu để người chơi
        nhận ra đây là một bridge đang thu vào.
        """

        top, right, bottom, left = (
            self.get_tile_points(x, y)
        )

        # Không vẽ mặt tile và cũng không vẽ hố đen.
        # Background phía sau chính là khoảng trống.

        # Bệ chứa bridge phía bên trái.
        source_anchor = [
            self.lerp_point(top, left, 0.60),
            self.lerp_point(top, left, 0.92),
            self.lerp_point(left, bottom, 0.08),
            self.lerp_point(left, bottom, 0.40),
        ]

        # Dấu neo nhỏ ở đầu đối diện.
        target_anchor = [
            self.lerp_point(top, right, 0.72),
            self.lerp_point(top, right, 0.92),
            self.lerp_point(right, bottom, 0.08),
            self.lerp_point(right, bottom, 0.28),
        ]

        pygame.draw.polygon(
            surface,
            theme.COLOR_BRIDGE_ANCHOR_TOP,
            source_anchor,
        )

        pygame.draw.polygon(
            surface,
            theme.COLOR_BRIDGE_ANCHOR_EDGE,
            source_anchor,
            width=2,
        )

        pygame.draw.polygon(
            surface,
            theme.COLOR_BRIDGE_ANCHOR_TOP,
            target_anchor,
        )

        pygame.draw.polygon(
            surface,
            theme.COLOR_BRIDGE_ANCHOR_EDGE,
            target_anchor,
            width=2,
        )
        
    def draw_open_bridge(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        progress: float,
    ) -> None:
        """
        Vẽ bridge trượt dần từ bệ bên trái sang đầu bên phải.

        progress:
            0.0 = thu hoàn toàn
            1.0 = mở hoàn toàn
        """

        progress = max(
            0.0,
            min(1.0, progress),
        )

        top, right, bottom, left = (
            self.get_tile_points(x, y)
        )

        # Luôn vẽ hai dấu neo.
        self.draw_closed_bridge(
            surface,
            x,
            y,
        )

        if progress <= 0.001:
            return

        # Bridge xuất phát từ cạnh top-left,
        # sau đó chạy về phía right-bottom.
        moving_top = self.lerp_point(
            top,
            right,
            progress,
        )

        moving_bottom = self.lerp_point(
            left,
            bottom,
            progress,
        )

        deck = [
            top,
            moving_top,
            moving_bottom,
            left,
        ]

        pygame.draw.polygon(
            surface,
            theme.COLOR_BRIDGE_DECK_TOP,
            deck,
        )

        pygame.draw.polygon(
            surface,
            theme.COLOR_BRIDGE_DECK_EDGE,
            deck,
            width=2,
        )

        # Các đường chia tấm chỉ xuất hiện khi bridge đã chạy tới.
        for fraction in (0.25, 0.50, 0.75):
            if fraction > progress:
                continue

            point_a = self.lerp_point(
                top,
                right,
                fraction,
            )

            point_b = self.lerp_point(
                left,
                bottom,
                fraction,
            )

            pygame.draw.line(
                surface,
                theme.COLOR_BRIDGE_PLANK_LINE,
                point_a,
                point_b,
                width=2,
            )

        # Hai rail chạy theo chiều dài bridge.
        pygame.draw.line(
            surface,
            theme.COLOR_BRIDGE_METAL_DARK,
            (top[0], top[1] + 3),
            (moving_top[0], moving_top[1] + 3),
            width=5,
        )

        pygame.draw.line(
            surface,
            theme.COLOR_BRIDGE_METAL_DARK,
            (left[0], left[1] + 3),
            (moving_bottom[0], moving_bottom[1] + 3),
            width=5,
        )

        pygame.draw.line(
            surface,
            theme.COLOR_BRIDGE_METAL,
            top,
            moving_top,
            width=3,
        )

        pygame.draw.line(
            surface,
            theme.COLOR_BRIDGE_METAL,
            left,
            moving_bottom,
            width=3,
        )
        
    