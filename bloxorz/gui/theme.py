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

# Thời gian chờ sau khi thắng trước khi tự động sang level tiếp theo.
AUTO_NEXT_LEVEL_DELAY = 1.2

# ---------------- LEVEL TRANSITION ----------------

# Thời gian màn hình tối dần sau khi hoàn thành level.
LEVEL_TRANSITION_FADE_OUT_DURATION = 0.6

# Thời gian giữ chữ LEVEL COMPLETE.
LEVEL_COMPLETE_HOLD_DURATION = 1.0

# Thời gian giữ tên level mới.
NEXT_LEVEL_HOLD_DURATION = 1.2

# Thời gian level mới hiện dần lên.
LEVEL_TRANSITION_FADE_IN_DURATION = 1

# Màu lớp phủ khi chuyển level.
LEVEL_TRANSITION_OVERLAY_COLOR = (8, 10, 16)

# Màu tiêu đề chuyển màn.
LEVEL_TRANSITION_TITLE_COLOR = (245, 185, 75)

# Màu mô tả level.
LEVEL_TRANSITION_SUBTITLE_COLOR = (225, 225, 230)

# ============================================================
# ADVANCED TILE COLORS
# ============================================================

# Fragile tile.
COLOR_FRAGILE_TOP = (218, 135, 68)
COLOR_FRAGILE_LEFT = (142, 76, 36)
COLOR_FRAGILE_RIGHT = (177, 96, 42)
COLOR_FRAGILE_CRACK = (82, 40, 24)
COLOR_FRAGILE_HIGHLIGHT = (248, 181, 102)

# Soft switch: nút tròn.
COLOR_SOFT_SWITCH_TOP = (255, 225, 55)
COLOR_SOFT_SWITCH_SIDE = (180, 145, 20)
COLOR_SOFT_SWITCH_EDGE = (90, 70, 15)
COLOR_SOFT_SWITCH_HIGHLIGHT = (255, 247, 155)

# Heavy switch: tấm chữ X.
COLOR_HEAVY_SWITCH_TOP = (230, 105, 32)
COLOR_HEAVY_SWITCH_SIDE = (135, 57, 18)
COLOR_HEAVY_SWITCH_EDGE = (70, 28, 12)
COLOR_HEAVY_SWITCH_HIGHLIGHT = (255, 175, 80)

# Bridge closed.
COLOR_BRIDGE_GAP = (22, 18, 17)
COLOR_BRIDGE_GAP_EDGE = (5, 5, 5)
COLOR_BRIDGE_ANCHOR_TOP = (105, 108, 110)
COLOR_BRIDGE_ANCHOR_EDGE = (48, 50, 52)

# Bridge open.
COLOR_BRIDGE_DECK_TOP = (145, 103, 61)
COLOR_BRIDGE_DECK_EDGE = (65, 42, 25)
COLOR_BRIDGE_PLANK_LINE = (82, 52, 30)
COLOR_BRIDGE_METAL = (175, 180, 182)
COLOR_BRIDGE_METAL_DARK = (65, 68, 70)

# Split switch để chuẩn bị cho bước sau.
COLOR_SPLIT_SWITCH = (104, 165, 240)
COLOR_SPLIT_SWITCH_EDGE = (31, 54, 105)

# ============================================================
# ADVANCED ANIMATIONS
# ============================================================

# Thời gian cầu trượt ra hoặc thu vào.
BRIDGE_ANIMATION_DURATION = 0.65

# Thời gian fragile bắt đầu nứt.
FRAGILE_CRACK_DURATION = 0.16

# Thời gian các mảnh fragile vỡ và rơi.
FRAGILE_SHATTER_DURATION = 0.55

# Thời gian block rơi sau khi tile đã vỡ.
FRAGILE_BLOCK_FALL_DURATION = 0.58

# Thời gian chờ trước khi reset.
FRAGILE_RESET_DELAY = 0.20

# Khoảng cách các mảnh và block rơi theo pixel.
FRAGILE_FALL_DISTANCE = 560

TUTORIAL_FADE_DURATION = 0.25