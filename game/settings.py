"""游戏配置常量 - 金属简约风（深蓝基色）"""
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

# ===== 基础文字色（深色面板上的浅色系）=====
WHITE = (236, 242, 250)
BLACK = (18, 28, 48)
DARK = (228, 236, 248)          # 主文字（浅色，用于深色金属面）
DARK2 = (176, 192, 218)         # 次要文字
MEDIUM = (132, 150, 180)        # 弱化文字
GRAY = (110, 126, 154)
LIGHT_GRAY = (168, 182, 206)
LIGHT = (214, 224, 238)
INK = (24, 36, 60)              # 银色金属按钮上的深色文字

# 统一金属描边色
OUTLINE = (22, 32, 52)

# ===== 背景（统一深蓝，同色系微渐变）=====
BG_TOP = (26, 42, 72)
BG_BOT = (16, 27, 50)
BG_COLOR = (20, 33, 58)

# ===== 深色钢面板 =====
PANEL = (46, 64, 98)
PANEL_SHADE = (28, 42, 70)
PANEL_LIGHT = (78, 98, 136)
METAL_RIM = (150, 168, 198)     # 银色金属包边

BOARD_BG = PANEL
GRID_COLOR = (56, 74, 108)
GRID_LINE_COLOR = (60, 80, 116)

# 棋盘格（深蓝同色系双色）
CELL_A = (40, 56, 88)
CELL_B = (33, 47, 77)

# ===== 金属色 =====
SILVER = (206, 216, 232)
SILVER_DARK = (128, 142, 166)
SILVER_LIGHT = (244, 247, 252)

# 唯一强调色：钢蓝
ACCENT_BLUE = (72, 146, 212)
ACCENT_BLUE_DARK = (38, 98, 158)
# 危险色（克制使用）
METAL_RED = (216, 88, 88)
METAL_RED_DARK = (150, 52, 56)
# 神秘关卡深石板色
SLATE = (72, 84, 118)
SLATE_DARK = (46, 56, 86)

# 兼容旧名称（金属简约：绿色=强调蓝，橙色=银，紫色=石板）
PLANK_BLUE = ACCENT_BLUE
PLANK_BLUE_DARK = ACCENT_BLUE_DARK
PLANK_GREEN = ACCENT_BLUE
PLANK_GREEN_DARK = ACCENT_BLUE_DARK
PLANK_ORANGE = SILVER
PLANK_ORANGE_DARK = SILVER_DARK
PLANK_RED = METAL_RED
PLANK_RED_DARK = METAL_RED_DARK
PLANK_PURPLE = SLATE
PLANK_PURPLE_DARK = SLATE_DARK

ACCENT = ACCENT_BLUE
ACCENT_LIGHT = (130, 190, 240)
ACCENT_DARK = ACCENT_BLUE_DARK
SUCCESS = ACCENT_BLUE
SUCCESS_DARK = ACCENT_BLUE_DARK
DANGER = METAL_RED
DANGER_DARK = METAL_RED_DARK
WARNING = SILVER
WARNING_DARK = SILVER_DARK

# 旧木质色 → 金属面板
WOOD_BROWN = PANEL
WOOD_DARK = PANEL_SHADE
WOOD_LIGHT = SILVER_LIGHT
WOOD_BORDER = METAL_RIM

# 星星（金属金/暗钢）
STAR_GOLD = (242, 190, 78)
STAR_EMPTY = (84, 100, 130)

# 箭头统一为金属银（方向由箭头形状区分）
ARROW_STEEL = (192, 206, 228)
ARROW_STEEL_DARK = (132, 148, 174)
ARROW_OUTLINE_COLOR = (50, 64, 90)
ARROW_UP_COLOR = ARROW_STEEL
ARROW_DOWN_COLOR = ARROW_STEEL
ARROW_LEFT_COLOR = ARROW_STEEL
ARROW_RIGHT_COLOR = ARROW_STEEL

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

# 神秘关卡（5x5 随机生成）的虚拟关卡索引
MYSTERY_LEVEL = -1
MYSTERY_MIN_ARROWS = 20
MYSTERY_HINTS = 3
NORMAL_HINTS = 1

# 存档文件路径
SAVE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "save_data.json")
