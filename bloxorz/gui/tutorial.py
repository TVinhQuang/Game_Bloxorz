from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pygame

from . import theme


@dataclass(frozen=True)
class TutorialPage:
    """
    Dữ liệu của một trang hướng dẫn.
    """

    title: str
    paragraphs: tuple[str, ...]
    tip: str
    visual_type: str


class TutorialOverlay:
    """
    Màn hình hướng dẫn nhiều trang.

    Chức năng:
    - Hiện tự động cho người chơi mới.
    - Điều hướng Back/Next.
    - Skip hoặc hoàn thành hướng dẫn.
    - Ghi nhớ trạng thái tutorial_seen trong file JSON.
    """

    def __init__(
        self,
        settings_path: str | Path,
    ) -> None:
        self.settings_path = Path(settings_path)

        self.pages = self._create_pages()

        self.page_index = 0
        self.active = not self._has_seen_tutorial()

        self.title_font = pygame.font.SysFont(
            "arial",
            38,
            bold=True,
        )

        self.page_number_font = pygame.font.SysFont(
            "arial",
            20,
            bold=True,
        )

        self.body_font = pygame.font.SysFont(
            "arial",
            21,
        )

        self.tip_font = pygame.font.SysFont(
            "arial",
            17,
            italic=True,
        )

        self.button_font = pygame.font.SysFont(
            "arial",
            19,
            bold=True,
        )

        self.small_font = pygame.font.SysFont(
            "arial",
            15,
        )

        # Rect của button được cập nhật mỗi lần draw().
        self.back_button = pygame.Rect(0, 0, 0, 0)
        self.next_button = pygame.Rect(0, 0, 0, 0)
        self.skip_button = pygame.Rect(0, 0, 0, 0)

    def _create_pages(self) -> list[TutorialPage]:
        """
        Create the English tutorial pages.
        """

        return [
            TutorialPage(
                title="Game Objective",
                paragraphs=(
                    "Roll the 1 x 1 x 2 block across the board and reach the green goal hole.",
                    "You complete a level only when the block is standing upright directly on the goal.",
                    "Lying horizontally or vertically across the goal does not complete the level.",
                ),
                tip=(
                    "Pay attention to the block orientation before approaching the goal."
                ),
                visual_type="goal",
            ),
            TutorialPage(
                title="Movement and Orientation",
                paragraphs=(
                    "Use WASD or the arrow keys to roll the block.",
                    "The block has three orientations: standing, horizontal, and vertical.",
                    "Every move may change its orientation, so plan several moves ahead.",
                ),
                tip=(
                    "Press a movement key once for each move. Holding a key does not repeatedly move the block."
                ),
                visual_type="controls",
            ),
            TutorialPage(
                title="Falling Off the Board",
                paragraphs=(
                    "Every cell occupied by the block must be fully supported.",
                    "The block falls if any part moves outside the board, onto a void, or onto a closed bridge.",
                    "After the falling animation, the current level automatically restarts.",
                ),
                tip=(
                    "A lying block occupies two cells, and both cells must be safe."
                ),
                visual_type="fall",
            ),
            TutorialPage(
                title="Advanced Tiles",
                paragraphs=(
                    "Fragile tile: the block may lie across it, but the tile breaks when the block stands upright on it.",
                    "Soft switch: activated whenever any part of the block or a split cube presses it.",
                    "Heavy switch: activated only when the complete block stands upright on it.",
                    "Bridge: a closed bridge behaves like a void; activate the correct switch to extend it.",
                    "Split switch: separates the block into two individually controlled cubes.",
                ),
                tip=(
                    "Recognize advanced tiles by their shapes and animations."
                ),
                visual_type="advanced",
            ),
            TutorialPage(
                title="Search Algorithms",
                paragraphs=(
                    "You may solve a level manually or run BFS, DFS, UCS, or A*.",
                    "A solver starts from the block's current state instead of returning to the start position.",
                    "BFS, UCS, and A* may find an optimal solution when every movement has equal cost.",
                    "DFS can find a solution, but it does not guarantee the shortest path.",
                ),
                tip=(
                    "Try solving the level manually before comparing your path with a search algorithm."
                ),
                visual_type="solver",
            ),
        ]

    def _has_seen_tutorial(self) -> bool:
        """
        Đọc trạng thái người chơi đã xem tutorial hay chưa.
        """

        if not self.settings_path.exists():
            return False

        try:
            with self.settings_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            return bool(
                data.get("tutorial_seen", False)
            )

        except (
            OSError,
            json.JSONDecodeError,
        ):
            return False

    def _mark_tutorial_seen(self) -> None:
        """
        Lưu tutorial_seen = true.

        Nếu file settings có dữ liệu khác thì vẫn giữ lại.
        """

        data: dict = {}

        if self.settings_path.exists():
            try:
                with self.settings_path.open(
                    "r",
                    encoding="utf-8",
                ) as file:
                    existing = json.load(file)

                if isinstance(existing, dict):
                    data.update(existing)

            except (
                OSError,
                json.JSONDecodeError,
            ):
                pass

        data["tutorial_seen"] = True

        try:
            self.settings_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with self.settings_path.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    data,
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

        except OSError:
            # Game vẫn chạy được ngay cả khi không ghi được settings.
            pass

    def open(self) -> None:
        """
        Mở lại hướng dẫn từ trang đầu.
        """

        self.page_index = 0
        self.active = True

    def close(
        self,
        mark_seen: bool = True,
    ) -> None:
        """
        Đóng hướng dẫn.
        """

        self.active = False

        if mark_seen:
            self._mark_tutorial_seen()

    def next_page(self) -> None:
        """
        Sang trang tiếp theo hoặc bắt đầu game ở trang cuối.
        """

        if self.page_index >= len(self.pages) - 1:
            self.close(mark_seen=True)
            return

        self.page_index += 1

    def previous_page(self) -> None:
        """
        Quay lại trang trước.
        """

        if self.page_index > 0:
            self.page_index -= 1

    def handle_key(self, key: int) -> None:
        """
        Điều khiển tutorial bằng bàn phím.
        """

        if key in (
            pygame.K_RIGHT,
            pygame.K_d,
            pygame.K_RETURN,
            pygame.K_SPACE,
        ):
            self.next_page()
            return

        if key in (
            pygame.K_LEFT,
            pygame.K_a,
        ):
            self.previous_page()
            return

        if key == pygame.K_ESCAPE:
            self.close(mark_seen=True)

    def handle_click(
        self,
        mouse_pos: tuple[int, int],
    ) -> None:
        """
        Điều khiển tutorial bằng chuột.
        """

        if self.back_button.collidepoint(mouse_pos):
            self.previous_page()
            return

        if self.next_button.collidepoint(mouse_pos):
            self.next_page()
            return

        if self.skip_button.collidepoint(mouse_pos):
            self.close(mark_seen=True)

    def draw(
        self,
        surface: pygame.Surface,
    ) -> None:
        """
        Vẽ tutorial lên trên toàn bộ game.
        """

        if not self.active:
            return

        width, height = surface.get_size()

        # Lớp nền tối.
        overlay = pygame.Surface(
            (width, height),
            pygame.SRCALPHA,
        )

        overlay.fill((0, 0, 0, 225))

        surface.blit(overlay, (0, 0))

        page = self.pages[self.page_index]

        margin_x = 54
        top_y = 44
        bottom_margin = 42

        page_number = (
            f"{self.page_index + 1}/"
            f"{len(self.pages)}"
        )

        page_number_surface = (
            self.page_number_font.render(
                page_number,
                True,
                (245, 195, 130),
            )
        )

        surface.blit(
            page_number_surface,
            (margin_x, top_y),
        )

        # Chia màn hình thành khu nội dung và khu minh họa.
        content_width = int(width * 0.58)

        content_rect = pygame.Rect(
            margin_x,
            top_y + 52,
            content_width,
            height - 210,
        )

        visual_rect = pygame.Rect(
            content_rect.right + 35,
            top_y + 70,
            width - content_rect.right - 85,
            height - 260,
        )

        # Title.
        title_surface = self.title_font.render(
            page.title,
            True,
            (245, 245, 240),
        )

        surface.blit(
            title_surface,
            (content_rect.x, content_rect.y),
        )

        current_y = content_rect.y + 68

        for paragraph in page.paragraphs:
            current_y = self._draw_wrapped_text(
                surface=surface,
                text=paragraph,
                font=self.body_font,
                color=(225, 225, 220),
                x=content_rect.x,
                y=current_y,
                max_width=content_rect.width,
                line_gap=7,
            )

            current_y += 22

        # Tip box.
        tip_rect = pygame.Rect(
            content_rect.x,
            min(
                current_y + 10,
                height - 205,
            ),
            content_rect.width,
            62,
        )

        pygame.draw.rect(
            surface,
            (48, 38, 30),
            tip_rect,
            border_radius=8,
        )

        pygame.draw.rect(
            surface,
            (170, 120, 70),
            tip_rect,
            width=1,
            border_radius=8,
        )

        tip_text = f"Tip: {page.tip}"

        self._draw_wrapped_text(
            surface=surface,
            text=tip_text,
            font=self.tip_font,
            color=(245, 205, 150),
            x=tip_rect.x + 14,
            y=tip_rect.y + 11,
            max_width=tip_rect.width - 28,
            line_gap=4,
        )

        # Khung minh họa.
        pygame.draw.rect(
            surface,
            (18, 18, 20),
            visual_rect,
            border_radius=14,
        )

        pygame.draw.rect(
            surface,
            (105, 82, 65),
            visual_rect,
            width=2,
            border_radius=14,
        )

        self._draw_visual(
            surface,
            visual_rect,
            page.visual_type,
        )

        # Buttons.
        button_y = height - bottom_margin - 46

        self.back_button = pygame.Rect(
            margin_x,
            button_y,
            135,
            42,
        )

        self.skip_button = pygame.Rect(
            width // 2 - 95,
            button_y,
            190,
            42,
        )

        self.next_button = pygame.Rect(
            width - margin_x - 165,
            button_y,
            165,
            42,
        )

        if self.page_index > 0:
            self._draw_button(
                surface,
                self.back_button,
                "Back",
            )

        self._draw_button(
            surface,
            self.skip_button,
            "Skip Instructions",
        )

        next_text = (
            "Start Game"
            if self.page_index == len(self.pages) - 1
            else "Next"
        )

        self._draw_button(
            surface,
            self.next_button,
            next_text,
        )

    def _draw_button(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        text: str,
    ) -> None:
        """
        Vẽ button tutorial.
        """

        hovered = rect.collidepoint(
            pygame.mouse.get_pos()
        )

        color = (
            (126, 76, 42)
            if hovered
            else (86, 55, 38)
        )

        pygame.draw.rect(
            surface,
            color,
            rect,
            border_radius=8,
        )

        pygame.draw.rect(
            surface,
            (218, 165, 105),
            rect,
            width=1,
            border_radius=8,
        )

        text_surface = self.button_font.render(
            text,
            True,
            (250, 240, 225),
        )

        surface.blit(
            text_surface,
            text_surface.get_rect(
                center=rect.center
            ),
        )

    def _draw_wrapped_text(
        self,
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        x: int,
        y: int,
        max_width: int,
        line_gap: int,
    ) -> int:
        """
        Tự xuống dòng dựa trên chiều rộng pixel.
        """

        words = text.split()

        current_line: list[str] = []
        lines: list[str] = []

        for word in words:
            test_line = " ".join(
                current_line + [word]
            )

            width = font.size(test_line)[0]

            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(
                        " ".join(current_line)
                    )

                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        current_y = y

        for line in lines:
            line_surface = font.render(
                line,
                True,
                color,
            )

            surface.blit(
                line_surface,
                (x, current_y),
            )

            current_y += (
                font.get_height() + line_gap
            )

        return current_y

    def _draw_visual(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        visual_type: str,
    ) -> None:
        """
        Chọn hình minh họa cho từng trang.
        """

        if visual_type == "goal":
            self._draw_goal_visual(
                surface,
                rect,
            )

        elif visual_type == "controls":
            self._draw_controls_visual(
                surface,
                rect,
            )

        elif visual_type == "fall":
            self._draw_fall_visual(
                surface,
                rect,
            )

        elif visual_type == "advanced":
            self._draw_advanced_visual(
                surface,
                rect,
            )

        elif visual_type == "solver":
            self._draw_solver_visual(
                surface,
                rect,
            )

    def _draw_goal_visual(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
    ) -> None:
        """
        Minh họa block đứng trên goal.
        """

        center_x = rect.centerx
        center_y = rect.centery + 70

        tile = [
            (center_x, center_y - 65),
            (center_x + 95, center_y - 15),
            (center_x, center_y + 35),
            (center_x - 95, center_y - 15),
        ]

        pygame.draw.polygon(
            surface,
            (90, 180, 110),
            tile,
        )

        pygame.draw.polygon(
            surface,
            (30, 80, 45),
            tile,
            width=3,
        )

        hole = [
            (
                center_x,
                center_y - 34,
            ),
            (
                center_x + 34,
                center_y - 15,
            ),
            (
                center_x,
                center_y + 4,
            ),
            (
                center_x - 34,
                center_y - 15,
            ),
        ]

        pygame.draw.polygon(
            surface,
            (12, 12, 12),
            hole,
        )

        block_rect = pygame.Rect(
            center_x - 32,
            center_y - 205,
            64,
            135,
        )

        pygame.draw.rect(
            surface,
            (132, 82, 55),
            block_rect,
            border_radius=4,
        )

        pygame.draw.rect(
            surface,
            (218, 145, 85),
            block_rect,
            width=3,
            border_radius=4,
        )

        text = self.small_font.render(
            "Stand upright to win",
            True,
            (245, 220, 185),
        )

        surface.blit(
            text,
            text.get_rect(
                center=(
                    center_x,
                    rect.bottom - 35,
                )
            ),
        )

    def _draw_controls_visual(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
    ) -> None:
        """
        Minh họa phím WASD và Arrow.
        """

        center_x = rect.centerx
        center_y = rect.centery

        key_size = 54
        gap = 9

        positions = {
            "W": (
                center_x - key_size // 2,
                center_y - key_size - gap,
            ),
            "A": (
                center_x - key_size - gap,
                center_y,
            ),
            "S": (
                center_x - key_size // 2,
                center_y,
            ),
            "D": (
                center_x + gap,
                center_y,
            ),
        }

        for label, position in positions.items():
            key_rect = pygame.Rect(
                position[0],
                position[1],
                key_size,
                key_size,
            )

            pygame.draw.rect(
                surface,
                (70, 72, 78),
                key_rect,
                border_radius=7,
            )

            pygame.draw.rect(
                surface,
                (180, 180, 185),
                key_rect,
                width=2,
                border_radius=7,
            )

            label_surface = (
                self.button_font.render(
                    label,
                    True,
                    (245, 245, 245),
                )
            )

            surface.blit(
                label_surface,
                label_surface.get_rect(
                    center=key_rect.center
                ),
            )

        caption = self.small_font.render(
            "WASD or Arrow Keys",
            True,
            (230, 215, 195),
        )

        surface.blit(
            caption,
            caption.get_rect(
                center=(
                    center_x,
                    rect.bottom - 48,
                )
            ),
        )

    def _draw_fall_visual(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
    ) -> None:
        """
        Minh họa block rơi khỏi map.
        """

        center_x = rect.centerx
        center_y = rect.centery - 10

        platform = pygame.Rect(
            center_x - 130,
            center_y - 15,
            180,
            42,
        )

        pygame.draw.rect(
            surface,
            (180, 185, 185),
            platform,
        )

        pygame.draw.rect(
            surface,
            (80, 85, 88),
            platform,
            width=3,
        )

        block = pygame.Rect(
            center_x + 45,
            center_y - 105,
            55,
            95,
        )

        pygame.draw.rect(
            surface,
            (132, 82, 55),
            block,
        )

        pygame.draw.line(
            surface,
            (235, 95, 70),
            (
                center_x + 73,
                center_y + 45,
            ),
            (
                center_x + 73,
                center_y + 135,
            ),
            width=6,
        )

        pygame.draw.polygon(
            surface,
            (235, 95, 70),
            [
                (
                    center_x + 58,
                    center_y + 118,
                ),
                (
                    center_x + 88,
                    center_y + 118,
                ),
                (
                    center_x + 73,
                    center_y + 142,
                ),
            ],
        )

    def _draw_advanced_visual(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
    ) -> None:
        """
        Minh họa bốn loại Advanced tile hiện có.
        """

        labels = [
            ("Fragile", "crack"),
            ("Soft", "circle"),
            ("Heavy", "x"),
            ("Bridge", "bridge"),
        ]

        columns = 2
        card_width = 120
        card_height = 105
        gap_x = 24
        gap_y = 20

        total_width = (
            columns * card_width
            + (columns - 1) * gap_x
        )

        start_x = (
            rect.centerx - total_width // 2
        )

        start_y = rect.centery - 120

        for index, (name, icon) in enumerate(labels):
            row = index // columns
            col = index % columns

            card = pygame.Rect(
                start_x
                + col * (card_width + gap_x),
                start_y
                + row * (card_height + gap_y),
                card_width,
                card_height,
            )

            pygame.draw.rect(
                surface,
                (38, 38, 42),
                card,
                border_radius=9,
            )

            pygame.draw.rect(
                surface,
                (105, 95, 88),
                card,
                width=1,
                border_radius=9,
            )

            icon_center = (
                card.centerx,
                card.y + 43,
            )

            if icon == "crack":
                pygame.draw.rect(
                    surface,
                    (215, 130, 65),
                    pygame.Rect(
                        icon_center[0] - 27,
                        icon_center[1] - 17,
                        54,
                        34,
                    ),
                )

                pygame.draw.line(
                    surface,
                    (75, 35, 22),
                    (
                        icon_center[0] - 20,
                        icon_center[1] - 10,
                    ),
                    (
                        icon_center[0] + 18,
                        icon_center[1] + 12,
                    ),
                    width=3,
                )

            elif icon == "circle":
                pygame.draw.ellipse(
                    surface,
                    (245, 215, 50),
                    pygame.Rect(
                        icon_center[0] - 28,
                        icon_center[1] - 14,
                        56,
                        28,
                    ),
                )

            elif icon == "x":
                pygame.draw.line(
                    surface,
                    (235, 105, 35),
                    (
                        icon_center[0] - 24,
                        icon_center[1] - 15,
                    ),
                    (
                        icon_center[0] + 24,
                        icon_center[1] + 15,
                    ),
                    width=8,
                )

                pygame.draw.line(
                    surface,
                    (235, 105, 35),
                    (
                        icon_center[0] + 24,
                        icon_center[1] - 15,
                    ),
                    (
                        icon_center[0] - 24,
                        icon_center[1] + 15,
                    ),
                    width=8,
                )

            elif icon == "bridge":
                pygame.draw.line(
                    surface,
                    (150, 105, 60),
                    (
                        icon_center[0] - 35,
                        icon_center[1],
                    ),
                    (
                        icon_center[0] + 35,
                        icon_center[1],
                    ),
                    width=14,
                )

            name_surface = self.small_font.render(
                name,
                True,
                (230, 225, 215),
            )

            surface.blit(
                name_surface,
                name_surface.get_rect(
                    center=(
                        card.centerx,
                        card.bottom - 20,
                    )
                ),
            )

    def _draw_solver_visual(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
    ) -> None:
        """
        Minh họa các thuật toán solver.
        """

        algorithms = [
            "BFS",
            "DFS",
            "UCS",
            "A*",
        ]

        center_x = rect.centerx
        start_y = rect.centery - 120

        for index, algorithm in enumerate(algorithms):
            algorithm_rect = pygame.Rect(
                center_x - 85,
                start_y + index * 62,
                170,
                44,
            )

            pygame.draw.rect(
                surface,
                (56, 61, 75),
                algorithm_rect,
                border_radius=8,
            )

            pygame.draw.rect(
                surface,
                (145, 155, 180),
                algorithm_rect,
                width=1,
                border_radius=8,
            )

            algorithm_surface = (
                self.button_font.render(
                    algorithm,
                    True,
                    (240, 240, 245),
                )
            )

            surface.blit(
                algorithm_surface,
                algorithm_surface.get_rect(
                    center=algorithm_rect.center
                ),
            )