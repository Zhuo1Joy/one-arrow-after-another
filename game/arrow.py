"""箭头类 - 圆润厚描边卡通风格"""
import pygame
import math
from game.settings import (
    ARROW_SIZE, CELL_SIZE,
    ARROW_UP_COLOR, ARROW_DOWN_COLOR, ARROW_LEFT_COLOR, ARROW_RIGHT_COLOR,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
    FLY_DURATION, BOUNCE_DURATION, BOUNCE_DISTANCE, BOUNCE_RETURN
)

# 金属描边色（深钢蓝）
ARROW_OUTLINE = (50, 64, 90)

SS = 2  # 超采样倍数
_ARROW_CACHE = {}


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


def draw_rounded_arrow(surface, cx, cy, size, color, direction, outline=ARROW_OUTLINE, alpha=255):
    """金属箭头：2x 超采样离屏绘制后平滑缩回（边缘无锯齿），表面按参数缓存"""
    size = max(8, int(size))
    a_key = 255 if alpha >= 252 else max(0, int(alpha)) // 16 * 16
    key = (size, tuple(color), direction, tuple(outline), a_key)
    img = _ARROW_CACHE.get(key)
    if img is None:
        half = size + 12
        box1 = half * 2
        big = pygame.Surface((box1 * SS, box1 * SS), pygame.SRCALPHA)
        bc = box1 * SS // 2
        s2 = size * SS
        pts = [(int(bc + rx * s2), int(bc + ry * s2)) for rx, ry in _arrow_raw_points(direction)]
        jr = max(2, size // 12) * SS
        grow = 1.0 + 4.6 / size
        cxm = sum(p[0] for p in pts) / len(pts)
        cym = sum(p[1] for p in pts) / len(pts)
        spts = [(int(cxm + (p[0] - cxm) * grow), int(cym + (p[1] - cym) * grow)) for p in pts]

        # 描边层（放大）→ 金属身体层
        _rounded_poly(big, spts, outline, jr)
        _rounded_poly(big, pts, color, jr)

        # 两层高光（柔光大斑 + 小亮斑，金属质感）
        hx_raw, hy_raw = -0.38, -0.24
        if direction == DIR_RIGHT:
            hx, hy = hx_raw, hy_raw
        elif direction == DIR_LEFT:
            hx, hy = -hx_raw, hy_raw
        elif direction == DIR_UP:
            hx, hy = hy_raw, -hx_raw
        else:
            hx, hy = -hy_raw, hx_raw
        hcx, hcy = int(bc + hx * s2), int(bc + hy * s2)
        soft = tuple(int(c + (255 - c) * 0.45) for c in color)
        bright = tuple(int(c + (255 - c) * 0.85) for c in color)
        pygame.draw.circle(big, soft, (hcx, hcy), max(2, size // 5 * SS))
        pygame.draw.circle(big, bright, (hcx - int(s2 * 0.05), hcy - int(s2 * 0.06)),
                           max(2, size // 11 * SS))

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
        center_x += self.fly_offset_x + self.bounce_offset_x
        center_y += self.fly_offset_y + self.bounce_offset_y

        color = self.DIRECTION_COLORS.get(self.direction, ARROW_RIGHT_COLOR)

        # 提示高亮：脉动金色光环（先画，让箭头身体压住重叠部分）
        if self.hint_timer > 0 and self.alive:
            pulse = 0.5 + 0.5 * math.sin(self.hint_timer * 11)
            rr = int(ARROW_SIZE * 0.72 + 4 * pulse)
            box = rr * 2 + 12
            glow = pygame.Surface((box, box), pygame.SRCALPHA)
            cc = box // 2
            alpha = int(120 + 110 * pulse)
            pygame.draw.circle(glow, (255, 205, 90, alpha), (cc, cc), rr, 5)
            pygame.draw.circle(glow, (255, 238, 170, int(alpha * 0.7)), (cc, cc), rr - 7, 3)
            surface.blit(glow, (int(center_x - cc), int(center_y - cc)))

        self._render(surface, center_x, center_y, color, self.alpha, getattr(self, 'scale', 1.0))

    def _render(self, surface, cx, cy, color, alpha=255, scale=1.0):
        """直接走超采样渲染（表面内部缓存）"""
        size = max(8, int((ARROW_SIZE // 2) * scale))
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
