"""箭头类 - 圆润厚描边卡通风格"""
import pygame
import math
from game.settings import (
    ARROW_SIZE, CELL_SIZE,
    ARROW_UP_COLOR, ARROW_DOWN_COLOR, ARROW_LEFT_COLOR, ARROW_RIGHT_COLOR,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
    FLY_DURATION, BOUNCE_DURATION, BOUNCE_DISTANCE, BOUNCE_RETURN
)

# 卡通描边色（与全局统一描边色一致）
ARROW_OUTLINE = (74, 62, 52)


def _arrow_raw_points(direction):
    """经典粗箭头造型（平尾+三角头，无深缺口），由向右基准形旋转/镜像得到"""
    base = [(1, 0), (0.02, -0.6), (-0.62, -0.6), (-0.62, 0.6), (0.02, 0.6)]
    if direction == DIR_RIGHT:
        return base
    if direction == DIR_LEFT:
        return [(-x, y) for x, y in base]
    if direction == DIR_UP:
        return [(y, -x) for x, y in base]
    return [(-y, x) for x, y in base]  # down


def _rounded_poly(surface, pts, color, joint_r):
    """带圆角顶点的实心多边形"""
    if len(pts) >= 3:
        pygame.draw.polygon(surface, color, pts)
    for p in pts:
        pygame.draw.circle(surface, color, (int(p[0]), int(p[1])), joint_r)


def draw_rounded_arrow(surface, cx, cy, size, color, direction, outline=ARROW_OUTLINE):
    """圆润厚描边卡通箭头：放大的描边层 + 原尺寸身体层（同形状嵌套，均匀厚边不变形）"""
    pts = [(int(cx + rx * size), int(cy + ry * size)) for rx, ry in _arrow_raw_points(direction)]
    jr = max(2, size // 12)        # 顶点圆角半径
    grow = 1.0 + 4.6 / size        # 描边层放大系数（边厚约 4~5px）

    cxm = sum(p[0] for p in pts) / len(pts)
    cym = sum(p[1] for p in pts) / len(pts)
    spts = [(int(cxm + (p[0] - cxm) * grow), int(cym + (p[1] - cym) * grow)) for p in pts]

    # 描边层（放大）→ 身体层（原尺寸）
    _rounded_poly(surface, spts, outline, jr)
    _rounded_poly(surface, pts, color, jr)

    # 尾部高光点（白色与身体色预先混合，避免透明叠加问题）
    hx_raw, hy_raw = -0.38, -0.24
    if direction == DIR_RIGHT:
        hx, hy = hx_raw, hy_raw
    elif direction == DIR_LEFT:
        hx, hy = -hx_raw, hy_raw
    elif direction == DIR_UP:
        hx, hy = hy_raw, -hx_raw
    else:
        hx, hy = -hy_raw, hx_raw
    hl = tuple(int(c + (255 - c) * 0.5) for c in color)
    pygame.draw.circle(surface, hl, (int(cx + hx * size), int(cy + hy * size)), max(2, size // 6))


class Arrow:
    """表示棋盘上的一个箭头"""

    DIRECTION_COLORS = {
        DIR_UP: ARROW_UP_COLOR,
        DIR_DOWN: ARROW_DOWN_COLOR,
        DIR_LEFT: ARROW_LEFT_COLOR,
        DIR_RIGHT: ARROW_RIGHT_COLOR,
    }

    def __init__(self, row, col, direction):
        self.row = row
        self.col = col
        self.direction = direction
        self.alive = True  # 是否还在棋盘上（用于路径检测）

        # 动画状态
        self.state = "idle"  # idle, flying, bouncing
        self.anim_timer = 0.0
        self.fly_offset_x = 0
        self.fly_offset_y = 0
        self.bounce_offset_x = 0
        self.bounce_offset_y = 0
        self.alpha = 255
        self.scale = 1.0  # 缩放比例（用于碰撞动画）

    def start_fly(self):
        """开始飞出动画（成功消除）"""
        self.state = "flying"
        self.anim_timer = 0.0
        self.alpha = 255
        self.alive = False  # 立即标记为不在棋盘上，避免阻挡其他箭头

    def start_bounce(self):
        """开始碰撞弹回动画"""
        self.state = "bouncing"
        self.anim_timer = 0.0
        self.bounce_offset_x = 0
        self.bounce_offset_y = 0
        self.scale = 1.0

    def update(self, dt):
        """更新动画状态"""
        if self.state == "flying":
            self.anim_timer += dt
            progress = min(self.anim_timer / FLY_DURATION, 1.0)

            fly_distance = 800  # 飞出距离（确保完全离开屏幕）
            if self.direction == DIR_RIGHT:
                self.fly_offset_x = fly_distance * progress
            elif self.direction == DIR_LEFT:
                self.fly_offset_x = -fly_distance * progress
            elif self.direction == DIR_DOWN:
                self.fly_offset_y = fly_distance * progress
            elif self.direction == DIR_UP:
                self.fly_offset_y = -fly_distance * progress

            self.alpha = int(255 * (1 - progress * 0.8))

            if progress >= 1.0:
                self.state = "idle"
                self.fly_offset_x = 0
                self.fly_offset_y = 0

        elif self.state == "bouncing":
            self.anim_timer += dt
            progress = min(self.anim_timer / BOUNCE_DURATION, 1.0)

            if progress < 1.0:
                # 先向前撞出，再弹回原位
                if progress < 0.4:
                    fly_progress = progress / 0.4
                    dist = BOUNCE_DISTANCE * fly_progress
                else:
                    return_progress = (progress - 0.4) / 0.6
                    ease = 1 - math.pow(1 - return_progress, 3)
                    dist = BOUNCE_DISTANCE * (1 - ease)

                if self.direction == DIR_RIGHT:
                    self.bounce_offset_x = dist
                elif self.direction == DIR_LEFT:
                    self.bounce_offset_x = -dist
                elif self.direction == DIR_DOWN:
                    self.bounce_offset_y = dist
                elif self.direction == DIR_UP:
                    self.bounce_offset_y = -dist

                # 碰撞缩放效果（挤压感）
                if progress < 0.2:
                    self.scale = 1.0 - 0.25 * (progress / 0.2)
                elif progress < 0.4:
                    self.scale = 0.75 + 0.25 * ((progress - 0.2) / 0.2)
                else:
                    self.scale = 1.0
            else:
                self.state = "idle"
                self.bounce_offset_x = 0
                self.bounce_offset_y = 0
                self.scale = 1.0

    def draw(self, surface, board_x, board_y):
        """绘制箭头"""
        if not self.alive and self.state != "flying":
            return

        center_x = board_x + self.col * CELL_SIZE + CELL_SIZE // 2
        center_y = board_y + self.row * CELL_SIZE + CELL_SIZE // 2
        center_x += self.fly_offset_x + self.bounce_offset_x
        center_y += self.fly_offset_y + self.bounce_offset_y

        color = self.DIRECTION_COLORS.get(self.direction, ARROW_RIGHT_COLOR)
        self._render(surface, center_x, center_y, color, self.alpha, getattr(self, 'scale', 1.0))

    def _render(self, surface, cx, cy, color, alpha=255, scale=1.0):
        """渲染圆润厚描边卡通箭头（离屏绘制后按整体透明度贴上）"""
        size = max(8, int((ARROW_SIZE // 2) * scale))
        pad = 60
        tmp = pygame.Surface((CELL_SIZE + pad * 2, CELL_SIZE + pad * 2), pygame.SRCALPHA)
        ox = oy = pad + CELL_SIZE // 2
        draw_rounded_arrow(tmp, ox, oy, size, color, self.direction)
        if alpha < 255:
            tmp.set_alpha(alpha)
        surface.blit(tmp, (int(cx - ox), int(cy - oy)))

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
        self.bounce_offset_x = 0
        self.bounce_offset_y = 0
        self.alpha = 255
        self.scale = 1.0
