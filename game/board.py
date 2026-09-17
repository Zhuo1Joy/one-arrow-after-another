"""棋盘类 - 玻璃果冻质感面板"""
import pygame
from game.settings import (
    BOARD_ROWS, BOARD_COLS, CELL_SIZE, BOARD_PADDING,
    OUTLINE, PANEL, PANEL_SHADE, CELL_A, CELL_B,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
)
from game.arrow import Arrow


class Board:
    """游戏棋盘"""

    def __init__(self, rows=BOARD_ROWS, cols=BOARD_COLS):
        self.rows = rows
        self.cols = cols
        self.arrows = []

    def load_level(self, level_data):
        """加载关卡数据，每个元素为 (row, col, direction)"""
        self.arrows = []
        for row, col, direction in level_data:
            self.arrows.append(Arrow(row, col, direction))

    def has_arrow(self, row, col):
        """检查指定位置是否有存活的箭头"""
        for arrow in self.arrows:
            if arrow.alive and arrow.row == row and arrow.col == col:
                return True
        return False

    def check_path_clear(self, arrow):
        """检查箭头前方路径是否畅通"""
        row, col, direction = arrow.row, arrow.col, arrow.direction

        if direction == DIR_RIGHT:
            for c in range(col + 1, self.cols):
                if self.has_arrow(row, c):
                    return False
        elif direction == DIR_LEFT:
            for c in range(col - 1, -1, -1):
                if self.has_arrow(row, c):
                    return False
        elif direction == DIR_DOWN:
            for r in range(row + 1, self.rows):
                if self.has_arrow(r, col):
                    return False
        elif direction == DIR_UP:
            for r in range(row - 1, -1, -1):
                if self.has_arrow(r, col):
                    return False
        return True

    def get_arrow_at(self, x, y, board_x, board_y):
        """获取指定位置的箭头"""
        for arrow in self.arrows:
            if arrow.alive and arrow.contains_point(x, y, board_x, board_y):
                return arrow
        return None

    def get_remaining_count(self):
        return sum(1 for arrow in self.arrows if arrow.alive)

    def is_cleared(self):
        return all(not arrow.alive for arrow in self.arrows)

    def update(self, dt):
        for arrow in self.arrows:
            arrow.update(dt)

    def draw(self, surface, board_x, board_y):
        """绘制玻璃果冻质感棋盘"""
        bw = self.cols * CELL_SIZE
        bh = self.rows * CELL_SIZE
        frame = 12  # 面板内边距

        fx, fy = board_x - frame, board_y - frame
        fw, fh = bw + frame * 2, bh + frame * 2
        r = 24

        # 面板离屏绘制（柔和投影 + 统一描边 + 果冻白面板）
        tmp = pygame.Surface((fw + 8, fh + 10), pygame.SRCALPHA)
        pygame.draw.rect(tmp, (60, 52, 45, 55), (4, 8, fw, fh), border_radius=r)
        pygame.draw.rect(tmp, OUTLINE, (0, 0, fw, fh), border_radius=r)
        fr = r - 5
        pygame.draw.rect(tmp, PANEL, (4, 4, fw - 8, fh - 8), border_radius=fr)
        surface.blit(tmp, (fx - 4, fy - 4))

        # 同色系双色棋盘格
        for row in range(self.rows):
            for col in range(self.cols):
                color = CELL_A if (row + col) % 2 == 0 else CELL_B
                pygame.draw.rect(surface, color,
                                 (board_x + col * CELL_SIZE, board_y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # 圆角遮罩环：盖住格子直角，让棋盘格区域保持圆润
        pygame.draw.rect(surface, PANEL, (fx + 4, fy + 4, fw - 8, fh - 8),
                         width=frame - 2, border_radius=fr)

        # 绘制所有箭头
        for arrow in self.arrows:
            arrow.draw(surface, board_x, board_y)

    def reset(self, level_data):
        self.load_level(level_data)
