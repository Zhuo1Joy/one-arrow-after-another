"""棋盘类"""
import pygame
from game.settings import (
    BOARD_ROWS, BOARD_COLS, CELL_SIZE, BOARD_PADDING,
    BOARD_BG, GRID_COLOR, WHITE, BLACK,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
)
from game.arrow import Arrow


class Board:
    """游戏棋盘"""

    def __init__(self, rows=BOARD_ROWS, cols=BOARD_COLS):
        """
        初始化棋盘
        :param rows: 行数
        :param cols: 列数
        """
        self.rows = rows
        self.cols = cols
        self.arrows = []

    def load_level(self, level_data):
        """
        加载关卡数据
        :param level_data: 关卡数据列表，每个元素为 (row, col, direction)
        """
        self.arrows = []
        for row, col, direction in level_data:
            arrow = Arrow(row, col, direction)
            self.arrows.append(arrow)

    def has_arrow(self, row, col):
        """检查指定位置是否有存活的箭头"""
        for arrow in self.arrows:
            if arrow.alive and arrow.row == row and arrow.col == col:
                return True
        return False

    def check_path_clear(self, arrow):
        """
        检查箭头前方路径是否畅通
        :param arrow: 要检查的箭头
        :return: True表示路径畅通，False表示有阻挡
        """
        row, col = arrow.row, arrow.col
        direction = arrow.direction

        if direction == DIR_RIGHT:
            # 检查右侧所有格子
            for c in range(col + 1, self.cols):
                if self.has_arrow(row, c):
                    return False
        elif direction == DIR_LEFT:
            # 检查左侧所有格子
            for c in range(col - 1, -1, -1):
                if self.has_arrow(row, c):
                    return False
        elif direction == DIR_DOWN:
            # 检查下方所有格子
            for r in range(row + 1, self.rows):
                if self.has_arrow(r, col):
                    return False
        elif direction == DIR_UP:
            # 检查上方所有格子
            for r in range(row - 1, -1, -1):
                if self.has_arrow(r, col):
                    return False

        return True

    def get_arrow_at(self, x, y, board_x, board_y):
        """
        获取指定位置的箭头
        :param x: 鼠标x坐标
        :param y: 鼠标y坐标
        :param board_x: 棋盘左上角x坐标
        :param board_y: 棋盘左上角y坐标
        :return: 箭头对象或None
        """
        for arrow in self.arrows:
            if arrow.alive and arrow.contains_point(x, y, board_x, board_y):
                return arrow
        return None

    def get_remaining_count(self):
        """获取剩余箭头数量"""
        return sum(1 for arrow in self.arrows if arrow.alive)

    def is_cleared(self):
        """检查是否所有箭头都已清除"""
        return all(not arrow.alive for arrow in self.arrows)

    def update(self, dt):
        """更新所有箭头的动画状态"""
        for arrow in self.arrows:
            arrow.update(dt)

    def draw(self, surface, board_x, board_y):
        """
        绘制棋盘和箭头
        :param surface: 目标surface
        :param board_x: 棋盘左上角x坐标
        :param board_y: 棋盘左上角y坐标
        """
        # 绘制棋盘背景
        board_width = self.cols * CELL_SIZE
        board_height = self.rows * CELL_SIZE
        pygame.draw.rect(surface, BOARD_BG, (board_x, board_y, board_width, board_height))

        # 绘制网格线
        for i in range(self.rows + 1):
            y = board_y + i * CELL_SIZE
            pygame.draw.line(surface, GRID_COLOR, (board_x, y), (board_x + board_width, y), 1)

        for i in range(self.cols + 1):
            x = board_x + i * CELL_SIZE
            pygame.draw.line(surface, GRID_COLOR, (x, board_y), (x, board_y + board_height), 1)

        # 绘制边框
        pygame.draw.rect(surface, BLACK, (board_x, board_y, board_width, board_height), 3)

        # 绘制所有箭头
        for arrow in self.arrows:
            arrow.draw(surface, board_x, board_y)

    def reset(self, level_data):
        """重置棋盘到初始状态"""
        self.load_level(level_data)
