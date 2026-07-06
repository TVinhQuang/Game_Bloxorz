"""
File theme.py chứa các hằng số dùng chung cho GUI.

Lý do tách riêng:
- Sau này muốn đổi màu/kích thước thì sửa một chỗ.
- renderer.py và app.py không bị ngập bởi hằng số giao diện.
"""


# =========================
# Window layout
# =========================

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 720

SIDE_PANEL_WIDTH = 310
MARGIN = 24

FPS = 60


# =========================
# Board / isometric layout
# =========================

ISO_TILE_WIDTH = 78
ISO_TILE_HEIGHT = 40
ISO_TILE_DEPTH = 14

MAX_TILE_SIZE = 64


# =========================
# Block size
# =========================

BLOCK_LYING_HEIGHT = 38
BLOCK_STANDING_HEIGHT = 86


# =========================
# Animation
# =========================

MOVE_ANIMATION_DURATION = 0.13

BLOCK_FALL_DURATION = 0.55
TILE_FALL_DURATION = 0.75
TILE_FALL_STAGGER = 0.035

FALL_DISTANCE = 520
RESET_AFTER_FALL_DELAY = 0.18


# =========================
# Button layout
# =========================

BUTTON_HEIGHT = 34
BUTTON_GAP = 8


# =========================
# Basic UI colors
# =========================

COLOR_BACKGROUND = (24, 26, 32)

COLOR_TEXT = (235, 235, 235)
COLOR_TEXT_MUTED = (170, 175, 185)

COLOR_ERROR = (240, 110, 110)
COLOR_SUCCESS = (110, 230, 140)


# =========================
# Bloxorz-style background
# =========================

COLOR_BACKGROUND_TOP = (185, 35, 5)
COLOR_BACKGROUND_MID = (125, 20, 5)
COLOR_BACKGROUND_BOTTOM = (45, 8, 4)

COLOR_SHADOW = (20, 5, 3, 95)


# =========================
# Panel / buttons
# =========================

COLOR_PANEL = (28, 30, 38)

COLOR_BUTTON = (54, 60, 76)
COLOR_BUTTON_HOVER = (74, 82, 104)
COLOR_BUTTON_BORDER = (120, 130, 155)


# =========================
# Old 2D fallback colors
# =========================

COLOR_VOID = (18, 20, 25)
COLOR_FLOOR = (95, 105, 120)
COLOR_START = (80, 140, 220)
COLOR_GOAL = (70, 180, 110)
COLOR_BLOCK = (230, 165, 60)
COLOR_BLOCK_BORDER = (255, 220, 120)


# =========================
# Tile colors
# =========================

COLOR_TILE_TOP = (190, 198, 198)
COLOR_TILE_LEFT = (105, 113, 116)
COLOR_TILE_RIGHT = (135, 144, 148)

COLOR_GRID_LINE = (88, 95, 98)


# =========================
# Start tile colors
# =========================

COLOR_START_TOP = (105, 155, 215)
COLOR_START_LEFT = (55, 95, 145)
COLOR_START_RIGHT = (70, 120, 175)


# =========================
# Goal tile colors
# =========================

COLOR_GOAL_TOP = (85, 190, 115)
COLOR_GOAL_LEFT = (38, 115, 65)
COLOR_GOAL_RIGHT = (50, 145, 80)

COLOR_GOAL_HOLE = (28, 20, 16)
COLOR_GOAL_HOLE_EDGE = (5, 5, 5)


# =========================
# Block colors
# =========================

COLOR_BLOCK_TOP = (132, 88, 62)
COLOR_BLOCK_LEFT = (82, 52, 40)
COLOR_BLOCK_RIGHT = (105, 62, 42)
COLOR_BLOCK_EDGE = (185, 125, 80)

COLOR_BLOCK_HIGHLIGHT = (185, 120, 75)
COLOR_BLOCK_DARK_STAIN = (45, 32, 28)