"""箭头类 - 人字形（chevron）扁平箭头"""
import pygame
import math
from game.settings import (
    ARROW_SIZE, CELL_SIZE,
    ARROW_UP_COLOR, ARROW_DOWN_COLOR, ARROW_LEFT_COLOR, ARROW_RIGHT_COLOR,
    ARROW_OUTLINE_COLOR,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
    FLY_DURATION, BOUNCE_DURATION, BOUNCE_DISTANCE, BOUNCE_RETURN
)

# 描边色（随主题切换）
ARROW_OUTLINE = ARROW_OUTLINE_COLOR

SS = 2  # 超采样倍数
_ARROW_CACHE = {}


def _arrow_raw_points(direction):
    """人字形（chevron，4 顶点）：尖 + 双翅 + 浅 V 口，由向右基准形旋转/镜像得到"""
    base = [(1.0, 0.0), (-1.0, -0.65), (-0.72, 0.0), (-1.0, 0.65)]
    if direction == DIR_RIGHT:
        return base
    if direction == DIR_LEFT:
        return [(-x, y) for x, y in base]
    if direction == DIR_UP:
        return [(y, -x) for x, y in base]
    return [(-y, x) for x, y in base]  # down


def draw_rounded_arrow(surface, cx, cy, size, color, direction, outline=ARROW_OUTLINE, alpha=255):
    """扁平三角箭头：2x 超采样后平滑缩回，纯色填充 + 黑色描边，表面按参数缓存"""
    size = max(8, int(size))
    a_key = 255 if alpha >= 252 else max(0, int(alpha)) // 16 * 16
    key = (size, tuple(color), direction, tuple(outline), a_key)
    img = _ARROW_CACHE.get(key)
    if img is None:
        half = size + 8
        box1 = half * 2
        big = pygame.Surface((box1 * SS, box1 * SS), pygame.SRCALPHA)
        bc = box1 * SS // 2
        s2 = size * SS
        pts = [(int(bc + rx * s2), int(bc + ry * s2)) for rx, ry in _arrow_raw_points(direction)]

        # 身体层 + 沿边描边（描边不超出顶点，尖端保持干净）
        pygame.draw.polygon(big, color, pts)
        pygame.draw.polygon(big, outline, pts, 2 * SS)

        img = pygame.transform.smoothscale(big, (box1, box1))
        if a_key < 255:
            img.set_alpha(a_key)
        if len(_ARROW_CACHE) < 600:
            _ARROW_CACHE[key] = img

    surface.blit(img, (int(cx) - img.get_width() // 2, int(cy) - img.get_height() // 2))


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
        self.hint_timer = 0.0  # 提示高亮剩余时间（脉动金色光环）

    def start_hint(self, duration=1.8):
        """开始提示高亮"""
        self.hint_timer = duration

    def clear_hint(self):
        self.hint_timer = 0.0

    def start_fly(self):
        """开始飞出动画（成功消除）"""
        self.state = "flying"
        self.anim_timer = 0.0
        self.alpha = 255
        self.alive = False  # 立即标记为不在棋盘上，避免阻挡其他箭头
        self.hint_timer = 0.0  # 飞出时取消提示光环

    def start_bounce(self):
        """开始碰撞弹回动画"""
        self.state = "bouncing"
        self.anim_timer = 0.0
        self.bounce_offset_x = 0
        self.bounce_offset_y = 0
        self.scale = 1.0

    def update(self, dt):
        """更新动画状态"""
        if self.hint_timer > 0:
            self.hint_timer = max(0.0, self.hint_timer - dt)

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
        # 与参考图一致：箭头位置向所指方向前移（纵向 8、横向 4）
        if self.direction == DIR_RIGHT:
            center_x += 4
        elif self.direction == DIR_LEFT:
            center_x -= 4
        elif self.direction == DIR_UP:
            center_y -= 8
        elif self.direction == DIR_DOWN:
            center_y += 8
        center_x += self.fly_offset_x + self.bounce_offset_x
        center_y += self.fly_offset_y + self.bounce_offset_y

        color = self.DIRECTION_COLORS.get(self.direction, ARROW_RIGHT_COLOR)

        # 提示高亮：脉动金色光环（先画，让箭头身体压住重叠部分）
        if self.hint_timer > 0 and self.alive:
            pulse = 0.5 + 0.5 * math.sin(self.hint_timer * 11)
            rr = int(ARROW_SIZE * 1.05 + 4 * pulse)
            box = rr * 2 + 12
            glow = pygame.Surface((box, box), pygame.SRCALPHA)
            cc = box // 2
            alpha = int(120 + 110 * pulse)
            pygame.draw.circle(glow, (255, 205, 90, alpha), (cc, cc), rr, 5)
            pygame.draw.circle(glow, (255, 238, 170, int(alpha * 0.7)), (cc, cc), rr - 7, 3)
            surface.blit(glow, (int(center_x - cc), int(center_y - cc)))

        self._render(surface, center_x, center_y, color, self.alpha, getattr(self, 'scale', 1.0))

    def _render(self, surface, cx, cy, color, alpha=255, scale=1.0):
        """直接走超采样渲染：纵向箭头略大于横向（与参考图一致）"""
        base_size = 21 if self.direction in (DIR_UP, DIR_DOWN) else 19
        size = max(8, int(base_size * scale))
        draw_rounded_arrow(surface, cx, cy, size, color, self.direction, alpha=int(alpha))

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
