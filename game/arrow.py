"""箭头类"""
import pygame
import math
from game.settings import (
    ARROW_SIZE, CELL_SIZE, RED, BLUE, GREEN, ORANGE,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
    FLY_DURATION, SHAKE_DURATION, SHAKE_INTENSITY
)


class Arrow:
    """表示棋盘上的一个箭头"""

    # 方向对应的颜色
    DIRECTION_COLORS = {
        DIR_UP: BLUE,
        DIR_DOWN: GREEN,
        DIR_LEFT: ORANGE,
        DIR_RIGHT: RED,
    }

    def __init__(self, row, col, direction):
        """
        初始化箭头
        :param row: 行索引
        :param col: 列索引
        :param direction: 方向 (up/down/left/right)
        """
        self.row = row
        self.col = col
        self.direction = direction
        self.alive = True  # 是否还在棋盘上

        # 动画状态
        self.state = "idle"  # idle, flying, shaking
        self.anim_timer = 0.0
        self.fly_offset_x = 0
        self.fly_offset_y = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.alpha = 255

    def start_fly(self):
        """开始飞出动画"""
        self.state = "flying"
        self.anim_timer = 0.0

    def start_shake(self):
        """开始晃动动画"""
        self.state = "shaking"
        self.anim_timer = 0.0

    def update(self, dt):
        """更新动画状态"""
        if self.state == "flying":
            self.anim_timer += dt
            progress = min(self.anim_timer / FLY_DURATION, 1.0)

            # 根据方向计算偏移
            fly_distance = 400  # 飞出距离
            if self.direction == DIR_RIGHT:
                self.fly_offset_x = fly_distance * progress
            elif self.direction == DIR_LEFT:
                self.fly_offset_x = -fly_distance * progress
            elif self.direction == DIR_DOWN:
                self.fly_offset_y = fly_distance * progress
            elif self.direction == DIR_UP:
                self.fly_offset_y = -fly_distance * progress

            # 透明度逐渐降低
            self.alpha = int(255 * (1 - progress))

            if progress >= 1.0:
                self.alive = False

        elif self.state == "shaking":
            self.anim_timer += dt
            progress = self.anim_timer / SHAKE_DURATION

            if progress < 1.0:
                # 晃动效果
                intensity = SHAKE_INTENSITY * (1 - progress)
                if self.direction in (DIR_LEFT, DIR_RIGHT):
                    self.shake_offset_y = math.sin(progress * math.pi * 4) * intensity
                else:
                    self.shake_offset_x = math.sin(progress * math.pi * 4) * intensity
            else:
                self.state = "idle"
                self.shake_offset_x = 0
                self.shake_offset_y = 0

    def draw(self, surface, board_x, board_y):
        """
        绘制箭头
        :param surface: 目标surface
        :param board_x: 棋盘左上角x坐标
        :param board_y: 棋盘左上角y坐标
        """
        if not self.alive and self.state != "flying":
            return

        # 计算箭头中心位置
        center_x = board_x + self.col * CELL_SIZE + CELL_SIZE // 2
        center_y = board_y + self.row * CELL_SIZE + CELL_SIZE // 2

        # 应用动画偏移
        center_x += self.fly_offset_x + self.shake_offset_x
        center_y += self.fly_offset_y + self.shake_offset_y

        # 获取颜色
        color = self.DIRECTION_COLORS.get(self.direction, RED)

        # 如果有alpha变化，创建新的surface
        if self.alpha < 255:
            arrow_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            self._draw_arrow(arrow_surface, CELL_SIZE // 2, CELL_SIZE // 2, color, self.alpha)
            surface.blit(arrow_surface, (center_x - CELL_SIZE // 2, center_y - CELL_SIZE // 2))
        else:
            self._draw_arrow(surface, center_x, center_y, color)

    def _draw_arrow(self, surface, cx, cy, color, alpha=255):
        """绘制箭头形状"""
        size = ARROW_SIZE // 2

        # 根据方向确定箭头顶点
        if self.direction == DIR_RIGHT:
            points = [
                (cx + size, cy),           # 箭头尖端
                (cx - size // 2, cy - size // 2),  # 左上
                (cx - size // 4, cy),      # 中间凹
                (cx - size // 2, cy + size // 2),  # 左下
            ]
        elif self.direction == DIR_LEFT:
            points = [
                (cx - size, cy),           # 箭头尖端
                (cx + size // 2, cy - size // 2),
                (cx + size // 4, cy),
                (cx + size // 2, cy + size // 2),
            ]
        elif self.direction == DIR_DOWN:
            points = [
                (cx, cy + size),           # 箭头尖端
                (cx - size // 2, cy - size // 2),
                (cx, cy - size // 4),
                (cx + size // 2, cy - size // 2),
            ]
        elif self.direction == DIR_UP:
            points = [
                (cx, cy - size),           # 箭头尖端
                (cx - size // 2, cy + size // 2),
                (cx, cy + size // 4),
                (cx + size // 2, cy + size // 2),
            ]

        # 应用alpha
        if alpha < 255:
            color_with_alpha = (*color, alpha)
            pygame.draw.polygon(surface, color_with_alpha, points)
        else:
            pygame.draw.polygon(surface, color, points)

        # 绘制边框
        border_color = (0, 0, 0, alpha) if alpha < 255 else (0, 0, 0)
        pygame.draw.polygon(surface, border_color, points, 2)

    def contains_point(self, x, y, board_x, board_y):
        """检测点是否在箭头单元格内"""
        cell_x = board_x + self.col * CELL_SIZE
        cell_y = board_y + self.row * CELL_SIZE
        return cell_x <= x < cell_x + CELL_SIZE and cell_y <= y < cell_y + CELL_SIZE

    def reset(self):
        """重置箭头状态"""
        self.alive = True
        self.state = "idle"
        self.anim_timer = 0.0
        self.fly_offset_x = 0
        self.fly_offset_y = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.alpha = 255
