from __future__ import annotations

from dataclasses import dataclass

import pygame

from . import theme


@dataclass
class Button:
    """
    Button đơn giản cho Pygame GUI.

    Mỗi button có:
    - rect: vùng hình chữ nhật để vẽ và bắt click
    - text: chữ hiển thị
    - action: mã hành động để app.py xử lý
    """

    rect: pygame.Rect
    text: str
    action: str

    def is_hovered(self, mouse_pos: tuple[int, int]) -> bool:
        # Kiểm tra chuột có nằm trong button không.
        return self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos: tuple[int, int]) -> bool:
        # Với button đơn giản, clicked nghĩa là vị trí click nằm trong rect.
        return self.rect.collidepoint(mouse_pos)

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        mouse_pos: tuple[int, int],
    ) -> None:
        """
        Vẽ button ra màn hình.

        surface:
            Màn hình Pygame hoặc một surface con.

        font:
            Font dùng để render text.

        mouse_pos:
            Vị trí chuột hiện tại để đổi màu hover.
        """

        # Nếu đang hover thì dùng màu sáng hơn.
        if self.is_hovered(mouse_pos):
            fill_color = theme.COLOR_BUTTON_HOVER
        else:
            fill_color = theme.COLOR_BUTTON

        # Vẽ thân button.
        pygame.draw.rect(
            surface,
            fill_color,
            self.rect,
            border_radius=8,
        )

        # Vẽ viền button.
        pygame.draw.rect(
            surface,
            theme.COLOR_BUTTON_BORDER,
            self.rect,
            width=1,
            border_radius=8,
        )

        # Render text của button.
        text_surface = font.render(
            self.text,
            True,
            theme.COLOR_TEXT,
        )

        # Căn giữa text trong button.
        text_rect = text_surface.get_rect(center=self.rect.center)

        # Vẽ text lên button.
        surface.blit(text_surface, text_rect)