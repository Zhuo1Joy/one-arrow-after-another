"""游戏配置常量"""
import os

# 窗口设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "一箭又一箭"

# 字体路径 (macOS 系统中文字体)
FONT_PATHS = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]

def get_font_path():
    """获取可用的中文字体路径"""
    for path in FONT_PATHS:
        if os.path.exists(path):
            return path
    return None

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
RED = (220, 50, 50)
GREEN = (50, 180, 50)
BLUE = (50, 100, 200)
YELLOW = (255, 200, 0)
ORANGE = (255, 140, 0)
BG_COLOR = (240, 240, 245)
BOARD_BG = (255, 255, 255)
GRID_COLOR = (220, 220, 220)

# 棋盘设置
BOARD_ROWS = 5
BOARD_COLS = 5
CELL_SIZE = 80
BOARD_PADDING = 20

# 游戏设置
MAX_MISTAKES = 3
ARROW_SIZE = 50

# 动画设置
FLY_DURATION = 0.3  # 飞出动画时长(秒)
SHAKE_DURATION = 0.5  # 晃动动画时长(秒)
SHAKE_INTENSITY = 8  # 晃动幅度(像素)

# 游戏状态
STATE_START = "start"
STATE_LEVEL_SELECT = "level_select"
STATE_PLAYING = "playing"
STATE_WIN = "win"
STATE_LOSE = "lose"
STATE_ALL_CLEAR = "all_clear"

# 方向定义
DIR_UP = "up"
DIR_DOWN = "down"
DIR_LEFT = "left"
DIR_RIGHT = "right"
