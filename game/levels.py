"""关卡数据"""
from game.settings import DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT

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
