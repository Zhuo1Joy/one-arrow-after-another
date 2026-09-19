"""游戏配置常量 - 简约扁平风（浅灰底 + 白底黑框棋盘 + 彩色箭头）"""
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
    for path in FONT_PATHS:
        if os.path.exists(path):
            return path
    return None

# ===== 文字色（浅灰底深色字）=====
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK = (30, 30, 30)            # 主文字（近黑）
DARK2 = (90, 90, 90)           # 次要文字
MEDIUM = (130, 130, 130)
GRAY = (160, 160, 160)
LIGHT_GRAY = (200, 200, 200)
LIGHT = (240, 240, 240)
INK = (20, 20, 20)

# 描边色（纯黑）
OUTLINE = (0, 0, 0)

# ===== 背景（纯色浅灰，带一点点蓝紫调）=====
BG_TOP = (240, 240, 245)
BG_BOT = (240, 240, 245)
BG_COLOR = (240, 240, 245)

# ===== 白色卡片面板 =====
PANEL = (255, 255, 255)
PANEL_SHADE = (220, 220, 220)
PANEL_LIGHT = (255, 255, 255)
METAL_RIM = (0, 0, 0)

BOARD_BG = PANEL
GRID_COLOR = (0, 0, 0)
GRID_LINE_COLOR = (229, 229, 229)

# 棋盘格（纯白，无棋盘双色）
CELL_A = (255, 255, 255)
CELL_B = (255, 255, 255)

# ===== 彩色按钮 =====
ACCENT_BLUE = (49, 100, 200)
ACCENT_BLUE_DARK = (30, 65, 150)
METAL_RED = (221, 50, 50)
METAL_RED_DARK = (170, 35, 35)
SLATE = (128, 128, 128)
SLATE_DARK = (60, 60, 60)

# 按钮黄（撤销键）
BUTTON_YELLOW = (255, 200, 3)
BUTTON_YELLOW_DARK = (205, 158, 0)

# 菜单灰
MENU_GRAY = (128, 128, 128)
MENU_GRAY_DARK = (100, 100, 100)
MENU_BORDER = (60, 60, 60)

SILVER = (200, 200, 200)
SILVER_DARK = (160, 160, 160)
SILVER_LIGHT = (240, 240, 240)

# 失误红色（与红色箭头一致）
MISTAKE_RED = (221, 50, 50)

# 兼容旧名称
PLANK_BLUE = ACCENT_BLUE
PLANK_BLUE_DARK = ACCENT_BLUE_DARK
PLANK_GREEN = (49, 181, 50)
PLANK_GREEN_DARK = (35, 140, 38)
PLANK_ORANGE = (255, 140, 0)
PLANK_ORANGE_DARK = (210, 112, 0)
PLANK_RED = METAL_RED
PLANK_RED_DARK = METAL_RED_DARK
PLANK_YELLOW = BUTTON_YELLOW
PLANK_YELLOW_DARK = BUTTON_YELLOW_DARK
PLANK_PURPLE = BUTTON_YELLOW
PLANK_PURPLE_DARK = BUTTON_YELLOW_DARK

ACCENT = ACCENT_BLUE
ACCENT_LIGHT = (120, 170, 230)
ACCENT_DARK = ACCENT_BLUE_DARK
SUCCESS = PLANK_GREEN
SUCCESS_DARK = PLANK_GREEN_DARK
DANGER = METAL_RED
DANGER_DARK = METAL_RED_DARK
WARNING = PLANK_ORANGE
WARNING_DARK = PLANK_ORANGE_DARK

WOOD_BROWN = PANEL
WOOD_DARK = PANEL_SHADE
WOOD_LIGHT = SILVER_LIGHT
WOOD_BORDER = OUTLINE

# 星星
STAR_GOLD = (240, 180, 40)
STAR_EMPTY = (200, 200, 200)

# 彩色箭头（方向区分颜色，与参考图一致）
ARROW_UP_COLOR = (49, 100, 200)        # 上：蓝
ARROW_DOWN_COLOR = (49, 181, 50)       # 下：绿
ARROW_LEFT_COLOR = (255, 140, 0)       # 左：橙
ARROW_RIGHT_COLOR = (221, 50, 50)      # 右：红
ARROW_OUTLINE_COLOR = (0, 0, 0)

# 棋盘设置
BOARD_ROWS = 5
BOARD_COLS = 5
CELL_SIZE = 80
BOARD_PADDING = 20

# 游戏设置
MAX_MISTAKES = 3
ARROW_SIZE = 30

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

# 神秘关卡（5x5 随机生成）的虚拟关卡索引
MYSTERY_LEVEL = -1
MYSTERY_MIN_ARROWS = 20
MYSTERY_HINTS = 3
NORMAL_HINTS = 1

# 存档文件路径
SAVE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "save_data.json")
