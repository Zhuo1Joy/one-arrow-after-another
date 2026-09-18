"""棋盘类 - 深蓝金属面板（底图超采样缓存）"""
import pygame
from game.settings import (
    BOARD_ROWS, BOARD_COLS, CELL_SIZE, BOARD_PADDING,
    PANEL, PANEL_SHADE, METAL_RIM, CELL_A, CELL_B, GRID_LINE_COLOR,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
)
from game.arrow import Arrow

SS = 2


class Board:
    """游戏棋盘"""

    def __init__(self, rows=BOARD_ROWS, cols=BOARD_COLS):
        self.rows = rows
        self.cols = cols
        self.arrows = []
        self._frame = self._build_frame()

    def _build_frame(self):
        """构建 2x 超采样的静态棋盘底图（包边+钢面板+棋盘格+网格），缩回 1x 缓存"""
        bw = self.cols * CELL_SIZE
        bh = self.rows * CELL_SIZE
        frame = 12
        fw, fh = bw + frame * 2, bh + frame * 2
        pw, ph = fw + 8, fh + 9

        big = pygame.Surface((pw * SS, ph * SS), pygame.SRCALPHA)
        r = 20 * SS
        fr = 16 * SS
        # 投影 + 银色金属包边 + 钢蓝面板
        pygame.draw.rect(big, (6, 12, 24, 120), (8, 14, fw * SS, fh * SS), border_radius=r)
        pygame.draw.rect(big, METAL_RIM, (0, 0, fw * SS, fh * SS), border_radius=r)
        pygame.draw.rect(big, PANEL, (6, 6, (fw - 6) * SS, (fh - 6) * SS), border_radius=fr)
        pygame.draw.line(big, (214, 226, 244, 130), (32, 12), (fw * SS - 32, 12), 4)

        # 棋盘格（表面内偏移 = frame+4 = 16）
        ox = (frame + 4) * SS
        for row in range(self.rows):
            for col in range(self.cols):
                color = CELL_A if (row + col) % 2 == 0 else CELL_B
                pygame.draw.rect(big, color,
                                 (ox + col * CELL_SIZE * SS, ox + row * CELL_SIZE * SS,
                                  CELL_SIZE * SS, CELL_SIZE * SS))

        # 内嵌边框遮罩环（盖住格子直角）；表面内偏移 (7,6)
        pygame.draw.rect(big, PANEL, (14, 12, (fw - 6) * SS, (fh - 6) * SS),
                         width=(frame - 2) * SS, border_radius=fr)

        # 细网格线（2x 下 2px，缩回后为柔细 1px）
        for i in range(1, self.rows):
            y = ox + i * CELL_SIZE * SS
            pygame.draw.line(big, GRID_LINE_COLOR, (ox, y), (ox + bw * SS, y), 2)
        for i in range(1, self.cols):
            x = ox + i * CELL_SIZE * SS
            pygame.draw.line(big, GRID_LINE_COLOR, (x, ox), (x, ox + bh * SS), 2)

        return pygame.transform.smoothscale(big, (pw, ph))

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
        """贴静态超采样底图 + 动态箭头"""
        frame = 12
        surface.blit(self._frame, (board_x - frame - 4, board_y - frame - 3))
        for arrow in self.arrows:
            arrow.draw(surface, board_x, board_y)

    def reset(self, level_data):
        self.load_level(level_data)
