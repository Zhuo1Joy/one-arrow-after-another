"""关卡数据"""
import random
from game.settings import (
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
    MYSTERY_MIN_ARROWS, BOARD_ROWS, BOARD_COLS,
)

# 关卡数据格式: [(row, col, direction), ...]
# 方向: "up", "down", "left", "right"

LEVELS = [
    # 关卡1 - 入门 (4个箭头)
    # 简单布局，大部分箭头可以直接飞出
    [
        (0, 0, DIR_RIGHT),   # 第一行第一个，向右
        (0, 3, DIR_UP),      # 第一行第四个，向上
        (2, 0, DIR_DOWN),    # 第三行第一个，向下
        (2, 3, DIR_LEFT),    # 第三行第四个，向左
    ],

    # 关卡2 - 进阶 (6个箭头)
    # 需要一定顺序才能通关
    [
        (0, 1, DIR_RIGHT),   # 第一行第二个，向右
        (1, 1, DIR_UP),      # 第二行第二个，向上
        (1, 3, DIR_DOWN),    # 第二行第四个，向下
        (3, 3, DIR_LEFT),    # 第四行第四个，向左
        (0, 0, DIR_DOWN),    # 第一行第一个，向下
        (2, 0, DIR_RIGHT),   # 第三行第一个，向右
    ],

    # 关卡3 - 挑战 (8个箭头)
    # 复杂布局，需要仔细思考顺序
    [
        (0, 0, DIR_RIGHT),   # 第一行第一个，向右
        (2, 2, DIR_UP),      # 第三行第三个，向上
        (1, 1, DIR_LEFT),    # 第二行第二个，向左
        (1, 0, DIR_DOWN),    # 第二行第一个，向下
        (1, 2, DIR_RIGHT),   # 第二行第三个，向右
        (3, 2, DIR_DOWN),    # 第四行第三个，向下
        (2, 3, DIR_LEFT),    # 第三行第四个，向左
        (3, 3, DIR_UP),      # 第四行第四个，向上
    ],
]


def get_level_count():
    """获取关卡总数"""
    return len(LEVELS)


def get_level(level_index):
    """
    获取指定关卡的数据
    :param level_index: 关卡索引 (0-based)
    :return: 关卡数据列表
    """
    if 0 <= level_index < len(LEVELS):
        return LEVELS[level_index]
    return None


def get_level_copy(level_index):
    """
    获取指定关卡数据的副本
    :param level_index: 关卡索引 (0-based)
    :return: 关卡数据副本
    """
    level = get_level(level_index)
    if level:
        return level.copy()
    return None


# ============ 神秘关卡随机生成 ============

_DIRS = (DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT)
_STEP = {DIR_UP: (-1, 0), DIR_DOWN: (1, 0), DIR_LEFT: (0, -1), DIR_RIGHT: (0, 1)}


def _lane_clear(row, col, direction, occupied, rows, cols):
    """检测在 (row,col) 朝 direction 到棋盘边缘之间是否没有已占据格子"""
    dr, dc = _STEP[direction]
    r, c = row + dr, col + dc
    while 0 <= r < rows and 0 <= c < cols:
        if (r, c) in occupied:
            return False
        r, c = r + dr, c + dc
    return True


def generate_mystery_level(rows=BOARD_ROWS, cols=BOARD_COLS):
    """
    生成必定有解的随机关卡。

    逆向构造：逐个放置箭头，每个新箭头的位置与方向完全随机，
    但只有"在当前已放置箭头中能正常飞出"时才接受。这样最后放入的
    箭头在开局时一定可飞出；按放置顺序的逆序移除即可全部消除。
    箭头数量随机（至少 MYSTERY_MIN_ARROWS 个），放置失败则整局重来。
    """
    while True:
        target = random.randint(MYSTERY_MIN_ARROWS, rows * cols)
        occupied = set()
        arrows = []
        ok = True

        for _ in range(target):
            free = [(r, c) for r in range(rows) for c in range(cols) if (r, c) not in occupied]
            placed = False
            for _try in range(400):
                r, c = random.choice(free)
                d = random.choice(_DIRS)
                if _lane_clear(r, c, d, occupied, rows, cols):
                    occupied.add((r, c))
                    arrows.append((r, c, d))
                    placed = True
                    break
            if not placed:
                ok = False
                break

        if ok and len(arrows) >= MYSTERY_MIN_ARROWS:
            return arrows
