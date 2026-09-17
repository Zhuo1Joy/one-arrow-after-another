"""游戏配置常量 - 统一色调果冻卡通风格"""
import os

# 窗口设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 650
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
    for path in FONT_PATHS:
        if os.path.exists(path):
            return path
    return None

# ===== 基础色 =====
WHITE = (255, 255, 255)
BLACK = (43, 38, 34)
DARK = (74, 62, 52)           # 正文深色
DARK2 = (94, 80, 68)
MEDIUM = (128, 116, 105)
GRAY = (172, 163, 152)
LIGHT_GRAY = (214, 208, 198)
LIGHT = (240, 238, 230)

# 统一卡通描边色（所有元素共用）
OUTLINE = (74, 62, 52)

# ===== 背景（单一柔和色调）=====
BG_TOP = (224, 241, 219)
BG_BOT = (183, 216, 180)
BG_COLOR = (204, 228, 198)

# ===== 面板（玻璃果冻白）=====
PANEL = (253, 253, 248)
PANEL_SHADE = (210, 224, 198)   # 面板底部内影
BOARD_BG = PANEL
GRID_COLOR = (236, 240, 226)
GRID_LINE_COLOR = (226, 232, 210)

# 棋盘格（同色系双色）
CELL_A = (250, 251, 242)
CELL_B = (234, 242, 224)

# ===== 果冻按钮色（统一饱和度与明度）=====
JELLY_GREEN = (128, 205, 112)
JELLY_GREEN_DARK = (86, 158, 74)
JELLY_BLUE = (112, 192, 232)
JELLY_BLUE_DARK = (64, 142, 184)
JELLY_ORANGE = (246, 180, 96)
JELLY_ORANGE_DARK = (204, 134, 56)
JELLY_RED = (242, 122, 112)
JELLY_RED_DARK = (196, 78, 70)
JELLY_PURPLE = (190, 142, 224)
JELLY_PURPLE_DARK = (142, 96, 182)

# 兼容旧名称
PLANK_BLUE = JELLY_BLUE
PLANK_BLUE_DARK = JELLY_BLUE_DARK
PLANK_GREEN = JELLY_GREEN
PLANK_GREEN_DARK = JELLY_GREEN_DARK
PLANK_ORANGE = JELLY_ORANGE
PLANK_ORANGE_DARK = JELLY_ORANGE_DARK
PLANK_RED = JELLY_RED
PLANK_RED_DARK = JELLY_RED_DARK
PLANK_PURPLE = JELLY_PURPLE
PLANK_PURPLE_DARK = JELLY_PURPLE_DARK

ACCENT = JELLY_BLUE
ACCENT_LIGHT = (170, 220, 244)
ACCENT_DARK = JELLY_BLUE_DARK
SUCCESS = JELLY_GREEN
SUCCESS_DARK = JELLY_GREEN_DARK
DANGER = JELLY_RED
DANGER_DARK = JELLY_RED_DARK
WARNING = JELLY_ORANGE
WARNING_DARK = JELLY_ORANGE_DARK

# 旧木质色 → 果冻中性面板
WOOD_BROWN = PANEL
WOOD_DARK = PANEL_SHADE
WOOD_LIGHT = WHITE
WOOD_BORDER = OUTLINE

# 星星
STAR_GOLD = (255, 202, 58)
STAR_EMPTY = (222, 218, 206)

# 箭头方向颜色 - 糖果色（统一饱和度与明度）
ARROW_UP_COLOR = (255, 122, 190)     # 糖果粉
ARROW_DOWN_COLOR = (96, 190, 255)    # 天空蓝
ARROW_LEFT_COLOR = (118, 214, 106)   # 苹果绿
ARROW_RIGHT_COLOR = (255, 168, 74)   # 杏橙

# 棋盘设置
BOARD_ROWS = 5
BOARD_COLS = 5
CELL_SIZE = 80
BOARD_PADDING = 20

# 游戏设置
MAX_MISTAKES = 3
ARROW_SIZE = 50

# 动画设置
FLY_DURATION = 0.35
BOUNCE_DURATION = 0.6
BOUNCE_DISTANCE = 60
BOUNCE_RETURN = 0.6
SCORE_ANIM_DURATION = 1.5

# 游戏状态
STATE_START = "start"
STATE_LEVEL_SELECT = "level_select"
STATE_PLAYING = "playing"
STATE_WIN = "win"
STATE_LOSE = "lose"
STATE_ALL_CLEAR = "all_clear"
STATE_LOAD_PROMPT = "load_prompt"

# 方向定义
DIR_UP = "up"
DIR_DOWN = "down"
DIR_LEFT = "left"
DIR_RIGHT = "right"

# 存档文件路径
SAVE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "save_data.json")
