"""游戏主逻辑 - 卡通木质风格（厚描边+木纹+森林场景）"""
import pygame
import json
import os
import time
import math
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, DARK, DARK2, MEDIUM, GRAY, LIGHT_GRAY, LIGHT, INK,
    OUTLINE, BG_TOP, BG_BOT, PANEL, PANEL_SHADE, SLATE, WOOD_DARK, WOOD_LIGHT, WOOD_BORDER,
    PLANK_BLUE, PLANK_BLUE_DARK, PLANK_GREEN, PLANK_GREEN_DARK,
    PLANK_ORANGE, PLANK_ORANGE_DARK, PLANK_RED, PLANK_RED_DARK, PLANK_PURPLE, PLANK_PURPLE_DARK,
    STAR_GOLD, STAR_EMPTY, MAX_MISTAKES, BOARD_ROWS, BOARD_COLS, CELL_SIZE,
    STATE_START, STATE_LEVEL_SELECT, STATE_PLAYING, STATE_WIN, STATE_LOSE, STATE_ALL_CLEAR, STATE_LOAD_PROMPT,
    get_font_path, SAVE_FILE, SCORE_ANIM_DURATION,
    ARROW_UP_COLOR, ARROW_DOWN_COLOR, ARROW_LEFT_COLOR, ARROW_RIGHT_COLOR,
    MYSTERY_LEVEL, MYSTERY_HINTS, NORMAL_HINTS,
)
from game.board import Board
from game.arrow import draw_rounded_arrow
from game.levels import get_level_copy, get_level_count, generate_mystery_level


# ============ 卡通绘制工具 ============

def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def render_text_outline(text, font, color, outline=OUTLINE, width=2):
    """渲染带描边的文字到带透明度的表面（可用于渐隐动画）"""
    if outline is OUTLINE:
        # 深色文字自动改用白色描边（贴纸效果），避免深底深字发糊
        lum = color[0] * 0.299 + color[1] * 0.587 + color[2] * 0.114
        if lum < 150:
            outline = WHITE
    base = font.render(text, True, color)
    ol = font.render(text, True, outline)
    w, h = base.get_width() + width * 2, base.get_height() + width * 2
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            if dx or dy:
                surf.blit(ol, (width + dx, width + dy))
    surf.blit(base, (width, width))
    return surf


def draw_text_outline(surface, text, font, color, center, outline=OUTLINE, width=2):
    """厚描边卡通文字"""
    surf = render_text_outline(text, font, color, outline, width)
    surface.blit(surf, surf.get_rect(center=center))


SS = 2  # 超采样倍数（SSAA，消除几何边缘锯齿）
_PLANK_CACHE = {}


def make_plank(w, h, base, dark, light, border):
    """金属质感面板（2x 超采样后平滑缩回，边缘细腻；同参数结果缓存）"""
    key = (int(w), int(h), tuple(base), tuple(dark), tuple(light), tuple(border))
    cached = _PLANK_CACHE.get(key)
    if cached is not None:
        return cached

    pw, ph = w + 8, h + 9
    big = pygame.Surface((pw * SS, ph * SS), pygame.SRCALPHA)
    r = max(10, min(16, h // 3)) * SS
    # 利落深色投影
    pygame.draw.rect(big, (6, 12, 24, 110), (8, 14, w * SS, h * SS), border_radius=r)
    # 金属包边
    pygame.draw.rect(big, border, (0, 0, w * SS, h * SS), border_radius=r)

    # 金属面：垂直微渐变（顶部略亮），用圆角 alpha mask 裁切
    fr = max(6, min(16, h // 3) - 4) * SS
    bw2, bh2 = (w - 6) * SS, (h - 6) * SS
    body = pygame.Surface((bw2, bh2), pygame.SRCALPHA)
    top_col = tuple(min(255, c + 16) for c in base)
    for yy in range(bh2):
        body.fill(lerp_color(top_col, base, (yy / bh2) * 0.7), (0, yy, bw2, 1))
    mask = pygame.Surface((bw2, bh2), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, bw2, bh2), border_radius=fr)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(body, (6, 6))

    # 底部斜面暗部（薄而利落的金属收边）
    band_h = max(5, (h - 6) // 4) * SS
    pygame.draw.rect(big, (*dark, 46), (12, h * SS - 6 - band_h, w * SS - 24, band_h),
                     border_top_left_radius=0, border_top_right_radius=0,
                     border_bottom_left_radius=max(0, fr - 6),
                     border_bottom_right_radius=max(0, fr - 6))
    # 顶部高光棱线 / 底部内反光线（2x 下线宽更顺滑）
    pygame.draw.line(big, (*light, 160), (24, 12), (w * SS - 24, 12), 3)
    pygame.draw.line(big, (*light, 50), (24, h * SS - 12), (w * SS - 24, h * SS - 12), 2)

    surf = pygame.transform.smoothscale(big, (pw, ph))
    _PLANK_CACHE[key] = surf
    return surf


def draw_heart(surface, cx, cy, size, color):
    """程序化红心（经典心形参数方程，2x 超采样 + 高光点）"""
    S = SS
    box = int(size * 2 + 6)
    big = pygame.Surface((box * S, box * S), pygame.SRCALPHA)
    bc = box * S // 2
    k = (size / 17.0) * S
    pts = []
    for i in range(60):
        t = 2 * math.pi * i / 60
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((bc + x * k, bc + (y - 2) * k))
    pygame.draw.polygon(big, color, pts)
    # 柔和高光
    hl = tuple(int(c + (255 - c) * 0.55) for c in color)
    pygame.draw.circle(big, hl, (int(bc - 5 * k), int(bc - 6 * k)), max(2, int(size * 0.22 * S)))
    small = pygame.transform.smoothscale(big, (box, box))
    surface.blit(small, (int(cx - box // 2), int(cy - box // 2)))


def draw_plank_button(surface, rect, base, dark, light, border, text="", font=None, text_color=None):
    """绘制金属按钮（文字颜色未指定时按金属面明度自动选择）"""
    surf = make_plank(rect.w, rect.h, base, dark, light, border)
    surface.blit(surf, (rect.x - 4, rect.y - 3))
    if text and font:
        if text_color is None:
            lum = base[0] * 0.299 + base[1] * 0.587 + base[2] * 0.114
            text_color = INK if lum > 150 else WHITE
        draw_text_outline(surface, text, font, text_color, rect.center)


def mini_arrow(surface, cx, cy, size, color, direction, outline=(50, 64, 90)):
    """装饰用金属小箭头"""
    draw_rounded_arrow(surface, cx, cy, size, color, direction, outline=outline)


# ============ 游戏主类 ============

class Game:
    """游戏主类"""

    def __init__(self):
        pygame.init()
        try:
            # SCALED：内部逻辑分辨率不变，GPU 线性缩放到窗口物理像素，高清屏更细腻
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED, vsync=1)
        except Exception:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("一箭又一箭")
        self.clock = pygame.time.Clock()

        font_path = get_font_path()
        self.font_title = pygame.font.Font(font_path, 52)
        self.font_large = pygame.font.Font(font_path, 38)
        self.font_medium = pygame.font.Font(font_path, 27)
        self.font_small = pygame.font.Font(font_path, 19)

        # 静态森林背景缓存
        self.bg_cache = self._build_background()

        self.state = STATE_START
        self.current_level = 0
        self.mistakes_left = MAX_MISTAKES
        self.board = Board()

        self.undo_available = True
        self.undo_history = None

        self.level_start_time = 0
        self.level_time = 0
        self.score = 0
        self.stars = 0
        self.score_animating = False
        self.score_anim_start = 0
        self.score_display = 0

        board_width = BOARD_COLS * CELL_SIZE
        board_height = BOARD_ROWS * CELL_SIZE
        self.board_x = (SCREEN_WIDTH - board_width) // 2
        self.board_y = (SCREEN_HEIGHT - board_height) // 2 + 24

        self.buttons = {}
        self.save_data = self.load_save_data()

        # 错误反馈：屏幕震动 + 浮动提示 + 红心闪烁
        self.shake_time = 0.0
        self.heart_flash = 0.0
        self.float_texts = []

        # 神秘关卡与提示
        self.is_mystery = False
        self.hints_left = 0
        self.hint_arrow = None

    # ---------- 背景 ----------

    def _build_background(self):
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        # 单一柔和色调渐变背景
        for y in range(SCREEN_HEIGHT):
            bg.fill(lerp_color(BG_TOP, BG_BOT, y / SCREEN_HEIGHT), (0, y, SCREEN_WIDTH, 1))
        return bg

    # ---------- 存档 ----------

    def load_save_data(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'stars' not in data:
                        data['stars'] = {}
                    if 'high_scores' not in data:
                        data['high_scores'] = {}
                    if 'level_states' not in data:
                        data['level_states'] = {}
                    return data
            except:
                pass
        return {'current_level': 0, 'level_states': {}, 'high_scores': {}, 'stars': {}}

    def save_to_file(self):
        try:
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.save_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存失败: {e}")

    def has_saved_game(self, level):
        return f"level_{level}" in self.save_data.get('level_states', {})

    def load_level_state(self, level):
        try:
            level_key = f"level_{level}"
            if level_key in self.save_data.get('level_states', {}):
                state = self.save_data['level_states'][level_key]
                arrows_data = []
                for arrow_data in state.get('arrows', []):
                    if isinstance(arrow_data, dict):
                        arrows_data.append((arrow_data['row'], arrow_data['col'], arrow_data['direction']))
                    elif isinstance(arrow_data, (list, tuple)) and len(arrow_data) >= 3:
                        arrows_data.append((arrow_data[0], arrow_data[1], arrow_data[2]))
                if not arrows_data:
                    return False
                self.board.load_level(arrows_data)
                self.mistakes_left = state.get('mistakes_left', MAX_MISTAKES)
                self.undo_available = state.get('undo_available', True)
                self.undo_history = None
                self.level_time = state.get('level_time', 0)
                self.level_start_time = time.time() - self.level_time
                for i, arrow_data in enumerate(state.get('arrows', [])):
                    if isinstance(arrow_data, dict) and not arrow_data.get('alive', True):
                        if i < len(self.board.arrows):
                            self.board.arrows[i].alive = False
                return True
        except Exception as e:
            print(f"加载存档失败: {e}")
        return False

    def save_level_state(self):
        level_key = f"level_{self.current_level}"
        if 'level_states' not in self.save_data:
            self.save_data['level_states'] = {}
        arrows_data = [{'row': a.row, 'col': a.col, 'direction': a.direction, 'alive': a.alive}
                       for a in self.board.arrows]
        self.save_data['level_states'][level_key] = {
            'arrows': arrows_data,
            'mistakes_left': self.mistakes_left,
            'undo_available': self.undo_available,
            'level_time': self.level_time
        }
        self.save_to_file()

    def update_high_score(self, level, score):
        level_key = f"level_{level}"
        if 'high_scores' not in self.save_data:
            self.save_data['high_scores'] = {}
        if score > self.save_data['high_scores'].get(level_key, 0):
            self.save_data['high_scores'][level_key] = score
            self.save_to_file()

    def get_high_score(self, level):
        return self.save_data.get('high_scores', {}).get(f"level_{level}", 0)

    def get_level_stars(self, level):
        return self.save_data.get('stars', {}).get(f"level_{level}", 0)

    def save_level_stars(self, level, stars):
        level_key = f"level_{level}"
        if 'stars' not in self.save_data:
            self.save_data['stars'] = {}
        if stars > self.save_data['stars'].get(level_key, 0):
            self.save_data['stars'][level_key] = stars
            self.save_to_file()

    # ---------- 主循环 ----------

    def start(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
            self.update(dt)
            self.draw()
        # 退出即清空存档：每次启动都从头开始
        self.clear_save_on_exit()
        pygame.quit()

    def clear_save_on_exit(self):
        try:
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
        except Exception as e:
            print(f"清空存档失败: {e}")
        self.save_data = {'current_level': 0, 'level_states': {}, 'high_scores': {}, 'stars': {}}

    def save_state(self):
        if self.undo_available:
            self.undo_history = {
                'arrows': [(a.row, a.col, a.direction, a.alive) for a in self.board.arrows],
                'mistakes_left': self.mistakes_left,
                'level_time': self.level_time
            }

    def undo(self):
        if self.undo_available and self.undo_history:
            self.board.arrows.clear()
            for row, col, direction, alive in self.undo_history['arrows']:
                from game.arrow import Arrow
                arrow = Arrow(row, col, direction)
                arrow.alive = alive
                self.board.arrows.append(arrow)
            self.mistakes_left = self.undo_history['mistakes_left']
            self.level_time = self.undo_history['level_time']
            self.undo_available = False
            self.undo_history = None
            self.hint_arrow = None

    def use_hint(self):
        """提示：找到第一个当前可以飞出的箭头并高亮（次数有限）"""
        if self.state != STATE_PLAYING or self.hints_left <= 0:
            return
        for arrow in self.board.arrows:
            if arrow.alive and self.board.check_path_clear(arrow):
                for other in self.board.arrows:
                    other.clear_hint()
                arrow.start_hint()
                self.hint_arrow = arrow
                self.hints_left -= 1
                return

    def handle_click(self, pos):
        x, y = pos
        if self.state == STATE_START:
            if "start" in self.buttons and self.buttons["start"].collidepoint(x, y):
                self.state = STATE_LEVEL_SELECT

        elif self.state == STATE_LEVEL_SELECT:
            for i in range(3):
                key = f"level_{i}"
                if key in self.buttons and self.buttons[key].collidepoint(x, y):
                    self.current_level = i
                    if self.has_saved_game(i):
                        self.state = STATE_LOAD_PROMPT
                    else:
                        self.load_level()
                    return
            if "mystery" in self.buttons and self.buttons["mystery"].collidepoint(x, y):
                self.start_mystery()
                return
            if "back" in self.buttons and self.buttons["back"].collidepoint(x, y):
                self.state = STATE_START

        elif self.state == STATE_LOAD_PROMPT:
            if "load_yes" in self.buttons and self.buttons["load_yes"].collidepoint(x, y):
                if self.load_level_state(self.current_level):
                    self.state = STATE_PLAYING
                else:
                    self.load_level()
                return
            if "load_no" in self.buttons and self.buttons["load_no"].collidepoint(x, y):
                self.load_level()
                return

        elif self.state == STATE_PLAYING:
            if "restart" in self.buttons and self.buttons["restart"].collidepoint(x, y):
                self.restart_level()
                return
            if "undo" in self.buttons and self.buttons["undo"].collidepoint(x, y) and self.undo_available and self.undo_history:
                self.undo()
                return
            if "hint" in self.buttons and self.buttons["hint"].collidepoint(x, y):
                self.use_hint()
                return
            if "back_to_menu" in self.buttons and self.buttons["back_to_menu"].collidepoint(x, y):
                if not self.is_mystery:
                    self.save_level_state()
                self.state = STATE_LEVEL_SELECT
                return
            arrow = self.board.get_arrow_at(x, y, self.board_x, self.board_y)
            if arrow:
                self.try_remove_arrow(arrow)

        elif self.state == STATE_WIN:
            if self.is_mystery:
                if "mystery_again" in self.buttons and self.buttons["mystery_again"].collidepoint(x, y):
                    self.start_mystery()
                elif "menu_win" in self.buttons and self.buttons["menu_win"].collidepoint(x, y):
                    self.state = STATE_LEVEL_SELECT
            else:
                for key, action in [("next", self.next_level), ("restart_win", self.restart_level),
                                    ("menu_win", lambda: setattr(self, 'state', STATE_LEVEL_SELECT))]:
                    if key in self.buttons and self.buttons[key].collidepoint(x, y):
                        action()

        elif self.state == STATE_LOSE:
            for key, action in [("restart_lose", self.restart_level),
                                ("menu_lose", lambda: setattr(self, 'state', STATE_LEVEL_SELECT))]:
                if key in self.buttons and self.buttons[key].collidepoint(x, y):
                    action()

        elif self.state == STATE_ALL_CLEAR:
            if "menu" in self.buttons and self.buttons["menu"].collidepoint(x, y):
                self.state = STATE_LEVEL_SELECT

    def load_level(self):
        level_data = get_level_copy(self.current_level)
        if level_data:
            self.is_mystery = False
            self.board.load_level(level_data)
            self.mistakes_left = MAX_MISTAKES
            self.undo_available = True
            self.undo_history = None
            self.level_start_time = time.time()
            self.level_time = 0
            self.hints_left = NORMAL_HINTS
            self.hint_arrow = None
            self.state = STATE_PLAYING
        else:
            self.state = STATE_ALL_CLEAR

    def start_mystery(self):
        """开始神秘关卡：随机生成一局全新的 5x5 关卡"""
        self.current_level = MYSTERY_LEVEL
        self.is_mystery = True
        self.board.load_level(generate_mystery_level())
        self.mistakes_left = MAX_MISTAKES
        self.undo_available = True
        self.undo_history = None
        self.level_start_time = time.time()
        self.level_time = 0
        self.hints_left = MYSTERY_HINTS
        self.hint_arrow = None
        self.state = STATE_PLAYING

    def restart_level(self):
        if self.is_mystery:
            self.start_mystery()
        else:
            self.load_level()

    def next_level(self):
        self.current_level += 1
        self.load_level()

    def calculate_score(self):
        base_score = 1000
        time_bonus = max(0, int(500 - self.level_time * 10))
        self.stars = max(0, 3 - (MAX_MISTAKES - self.mistakes_left))
        self.score = base_score + time_bonus + self.stars * 200

    def try_remove_arrow(self, arrow):
        self.save_state()
        if self.board.check_path_clear(arrow):
            arrow.start_fly()
        else:
            arrow.start_bounce()
            self.mistakes_left -= 1
            # 明显的错误提示：屏幕震动 + "挡住了！"浮动文字 + 红心闪烁
            self.shake_time = 0.3
            self.heart_flash = 0.8
            ax = self.board_x + arrow.col * CELL_SIZE + CELL_SIZE // 2
            ay = self.board_y + arrow.row * CELL_SIZE - 12
            self.float_texts.append({'text': "挡住了！", 'x': ax, 'y': ay,
                                     'born': time.time(), 'color': (255, 110, 110)})
            if self.mistakes_left <= 0:
                self.state = STATE_LOSE

    def update(self, dt):
        # 反馈计时器
        if self.shake_time > 0:
            self.shake_time = max(0.0, self.shake_time - dt)
        if self.heart_flash > 0:
            self.heart_flash = max(0.0, self.heart_flash - dt)
        now = time.time()
        self.float_texts = [ft for ft in self.float_texts if now - ft['born'] <= 0.9]

        if self.state == STATE_PLAYING:
            self.board.update(dt)
            self.level_time = time.time() - self.level_start_time
            if self.board.is_cleared():
                if self.is_mystery:
                    # 神秘关卡：无星级、无分数
                    self.state = STATE_WIN
                else:
                    self.calculate_score()
                    self.update_high_score(self.current_level, self.score)
                    self.save_level_stars(self.current_level, self.stars)
                    level_key = f"level_{self.current_level}"
                    if level_key in self.save_data.get('level_states', {}):
                        del self.save_data['level_states'][level_key]
                        self.save_to_file()
                    if self.current_level + 1 < get_level_count():
                        self.state = STATE_WIN
                    else:
                        self.state = STATE_ALL_CLEAR
                    self.score_animating = True
                    self.score_anim_start = time.time()
                    self.score_display = 0
        if self.score_animating:
            elapsed = time.time() - self.score_anim_start
            progress = min(elapsed / SCORE_ANIM_DURATION, 1.0)
            ease = 1 - math.pow(1 - progress, 3)
            self.score_display = int(self.score * ease)
            if progress >= 1.0:
                self.score_animating = False
                self.score_display = self.score

    # ---------- 绘制 ----------

    def draw(self):
        self.buttons = {}
        self.screen.blit(self.bg_cache, (0, 0))

        if self.state == STATE_START:
            self.draw_start_screen()
        elif self.state == STATE_LEVEL_SELECT:
            self.draw_level_select_screen()
        elif self.state == STATE_LOAD_PROMPT:
            self.draw_load_prompt()
        elif self.state == STATE_PLAYING:
            self.draw_game_screen()
        elif self.state == STATE_WIN:
            self.draw_game_screen()
            self.draw_win_overlay()
        elif self.state == STATE_LOSE:
            self.draw_game_screen()
            self.draw_lose_overlay()
        elif self.state == STATE_ALL_CLEAR:
            self.draw_all_clear_screen()

        pygame.display.flip()

    def draw_start_screen(self):
        # 标题果冻面板
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 210, 92, 420, 96)
        draw_plank_button(self.screen, panel, PANEL, PANEL_SHADE, WHITE, OUTLINE)
        draw_text_outline(self.screen, "一箭又一箭", self.font_title, DARK,
                          (SCREEN_WIDTH // 2, 140), width=3)

        # 副标题
        draw_text_outline(self.screen, "点击箭头 让它飞出棋盘", self.font_small, DARK2,
                          (SCREEN_WIDTH // 2, 225))

        # 四个彩色装饰箭头
        ay = 278
        cx0 = SCREEN_WIDTH // 2 - 120
        for i, (col, d) in enumerate([(ARROW_UP_COLOR, "up"), (ARROW_RIGHT_COLOR, "right"),
                                      (ARROW_DOWN_COLOR, "down"), (ARROW_LEFT_COLOR, "left")]):
            mini_arrow(self.screen, cx0 + i * 80, ay, 26, col, d)

        # 开始按钮
        btn = pygame.Rect(SCREEN_WIDTH // 2 - 140, 330, 280, 76)
        draw_plank_button(self.screen, btn, PLANK_GREEN, PLANK_GREEN_DARK, WHITE, OUTLINE,
                          "开始游戏", self.font_large)
        self.buttons["start"] = btn

        # 提示
        draw_text_outline(self.screen, "提示：路径上有箭头挡路就飞不出去哦", self.font_small, DARK2,
                          (SCREEN_WIDTH // 2, 448))

    def draw_level_select_screen(self):
        # 标题果冻面板
        title = pygame.Rect(SCREEN_WIDTH // 2 - 160, 48, 320, 70)
        draw_plank_button(self.screen, title, PANEL, PANEL_SHADE, WHITE, OUTLINE)
        draw_text_outline(self.screen, "选择关卡", self.font_large, DARK,
                          (SCREEN_WIDTH // 2, 83), width=3)

        # 三个关卡按钮
        bw, bh, gap = 170, 80, 34
        total = 3 * bw + 2 * gap
        sx = (SCREEN_WIDTH - total) // 2
        by = 190
        planks = [(PLANK_BLUE, PLANK_BLUE_DARK), (PLANK_GREEN, PLANK_GREEN_DARK), (PLANK_ORANGE, PLANK_ORANGE_DARK)]
        for i in range(3):
            bx = sx + i * (bw + gap)
            rect = pygame.Rect(bx, by, bw, bh)
            base, dk = planks[i]
            draw_plank_button(self.screen, rect, base, dk, WHITE, OUTLINE,
                              f"关卡 {i + 1}", self.font_medium)
            self.buttons[f"level_{i}"] = rect

            # 最高分（按钮上方）
            hs = self.get_high_score(i)
            if hs > 0:
                draw_text_outline(self.screen, f"最高 {hs}", self.font_small, DARK2,
                                  (bx + bw // 2, by - 22))

            # 实心星星
            stars = self.get_level_stars(i)
            ss, sgap = 22, 8
            sw = 3 * ss + 2 * sgap
            for j in range(3):
                scx = bx + (bw - sw) // 2 + j * (ss + sgap) + ss // 2
                scy = by + bh + 28
                self.draw_star(scx, scy, ss // 2, STAR_GOLD if j < stars else STAR_EMPTY)

        # 神秘关卡
        my = by + 120
        mrect = pygame.Rect(SCREEN_WIDTH // 2 - 85, my, 170, 70)
        draw_plank_button(self.screen, mrect, PLANK_PURPLE, PLANK_PURPLE_DARK, WHITE, OUTLINE,
                          "? 神秘关卡", self.font_small)
        self.buttons["mystery"] = mrect

        # 返回
        back = pygame.Rect(SCREEN_WIDTH // 2 - 85, SCREEN_HEIGHT - 88, 170, 56)
        draw_plank_button(self.screen, back, PANEL, PANEL_SHADE, WHITE, OUTLINE,
                          "返回", self.font_medium, DARK)
        self.buttons["back"] = back

    def draw_load_prompt(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(SCREEN_WIDTH // 2 - 215, SCREEN_HEIGHT // 2 - 145, 430, 290)
        draw_plank_button(self.screen, panel, PANEL, PANEL_SHADE, WHITE, WOOD_BORDER)

        draw_text_outline(self.screen, f"发现关卡 {self.current_level + 1} 的存档",
                          self.font_medium, DARK, (panel.centerx, panel.y + 62), width=2)
        draw_text_outline(self.screen, "是否加载上次的游戏进度？",
                          self.font_small, DARK2, (panel.centerx, panel.y + 112))

        bw, bh = 150, 54
        by = panel.y + 175
        yes = pygame.Rect(panel.centerx - bw - 18, by, bw, bh)
        draw_plank_button(self.screen, yes, PLANK_GREEN, PLANK_GREEN_DARK, WOOD_LIGHT, WOOD_BORDER,
                          "加载存档", self.font_small)
        self.buttons["load_yes"] = yes

        no = pygame.Rect(panel.centerx + 18, by, bw, bh)
        draw_plank_button(self.screen, no, PLANK_ORANGE, PLANK_ORANGE_DARK, WOOD_LIGHT, WOOD_BORDER,
                          "重新开始", self.font_small)
        self.buttons["load_no"] = no

    def draw_game_screen(self):
        # 顶部果冻信息条
        bar = pygame.Rect(-4, 6, SCREEN_WIDTH + 8, 56)
        draw_plank_button(self.screen, bar, PANEL, PANEL_SHADE, WHITE, OUTLINE)

        back = pygame.Rect(14, 15, 78, 38)
        draw_plank_button(self.screen, back, PLANK_RED, PLANK_RED_DARK, WHITE, OUTLINE,
                          "菜单", self.font_small)
        self.buttons["back_to_menu"] = back

        level_label = "神秘关卡" if self.is_mystery else f"关卡 {self.current_level + 1}"
        draw_text_outline(self.screen, level_label, self.font_small,
                          DARK, (135, 34))
        draw_text_outline(self.screen, f"剩余 {self.board.get_remaining_count()}",
                          self.font_small, DARK, (SCREEN_WIDTH // 2 - 90, 34))
        draw_text_outline(self.screen, f"时间 {int(self.level_time)}s", self.font_small,
                          DARK, (SCREEN_WIDTH // 2 + 60, 34))
        hcol = (240, 92, 84)
        if self.heart_flash > 0 and int(self.heart_flash * 10) % 2 == 0:
            hcol = (130, 32, 28)
        n = max(0, self.mistakes_left)
        hx0 = SCREEN_WIDTH - 118
        for i in range(n):
            draw_heart(self.screen, hx0 + i * 26, 34, 11, hcol)

        # 棋盘（受撞击时震动）
        dx = dy = 0
        if self.shake_time > 0:
            amp = 6 * (self.shake_time / 0.3)
            dx = int(amp * math.sin(self.shake_time * 55))
            dy = int(amp * 0.6 * math.cos(self.shake_time * 47))
        self.board.draw(self.screen, self.board_x + dx, self.board_y + dy)

        # 底部按钮（重新开始 / 撤销 / 提示）
        by = self.board_y + BOARD_ROWS * CELL_SIZE + 24
        bw, bh, gap = 130, 54, 14
        sx = (SCREEN_WIDTH - (bw * 3 + gap * 2)) // 2
        restart = pygame.Rect(sx, by, bw, bh)
        draw_plank_button(self.screen, restart, PLANK_BLUE, PLANK_BLUE_DARK, WHITE, OUTLINE,
                          "重新开始", self.font_small)
        self.buttons["restart"] = restart

        undo = pygame.Rect(sx + bw + gap, by, bw, bh)
        if self.undo_available and self.undo_history:
            draw_plank_button(self.screen, undo, PLANK_ORANGE, PLANK_ORANGE_DARK, WHITE, OUTLINE,
                              "撤销 (1次)", self.font_small)
        else:
            draw_plank_button(self.screen, undo, (150, 160, 180), (106, 118, 140), WHITE, WOOD_BORDER,
                              "撤销 (1次)", self.font_small, GRAY)
        self.buttons["undo"] = undo

        hint_btn = pygame.Rect(sx + (bw + gap) * 2, by, bw, bh)
        if self.hints_left > 0:
            draw_plank_button(self.screen, hint_btn, SLATE, OUTLINE, WHITE, OUTLINE,
                              f"提示 ({self.hints_left})", self.font_small)
        else:
            draw_plank_button(self.screen, hint_btn, (150, 160, 180), (106, 118, 140), WHITE, WOOD_BORDER,
                              f"提示 (0)", self.font_small, GRAY)
        self.buttons["hint"] = hint_btn

        # 上浮渐隐的错误提示
        self._draw_float_texts()

    def _draw_float_texts(self):
        """上浮渐隐的提示文字"""
        now = time.time()
        for ft in self.float_texts:
            t = now - ft['born']
            if t < 0 or t > 0.9:
                continue
            prog = t / 0.9
            surf = render_text_outline(ft['text'], self.font_medium, ft['color'], width=3)
            if prog > 0.55:
                surf.set_alpha(int(255 * (1 - (prog - 0.55) / 0.45)))
            self.screen.blit(surf, surf.get_rect(center=(ft['x'], int(ft['y'] - 36 * prog))))

    def _dim(self, alpha=140):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))

    def draw_win_overlay(self):
        if self.is_mystery:
            self.draw_mystery_win_overlay()
            return
        self._dim(150)
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 210, 55, 420, 520)
        draw_plank_button(self.screen, panel, PANEL, PANEL_SHADE, WHITE, WOOD_BORDER)

        # 标题绿木板
        t = pygame.Rect(SCREEN_WIDTH // 2 - 150, 82, 300, 66)
        draw_plank_button(self.screen, t, PLANK_GREEN, PLANK_GREEN_DARK, WOOD_LIGHT, WOOD_BORDER)
        draw_text_outline(self.screen, "恭喜通关!", self.font_large, WHITE, (t.centerx, t.centery), width=3)

        # 大星星（实心+描边+高光）
        ss = 52
        gap = 26
        sw = 3 * ss + 2 * gap
        for i in range(3):
            scx = SCREEN_WIDTH // 2 - sw // 2 + i * (ss + gap) + ss // 2
            self.draw_star(scx, 215, ss // 2, STAR_GOLD if i < self.stars else STAR_EMPTY, shine=True)

        draw_text_outline(self.screen, f"得分  {self.score_display}", self.font_large, WHITE,
                          (SCREEN_WIDTH // 2, 292), width=2)
        draw_text_outline(self.screen, f"用时  {int(self.level_time)} 秒", self.font_small,
                          DARK2, (SCREEN_WIDTH // 2, 338))
        hs = self.get_high_score(self.current_level)
        if hs > 0:
            draw_text_outline(self.screen, f"最高分  {hs}", self.font_small, (200, 150, 30),
                              (SCREEN_WIDTH // 2, 368))

        bw, bh = 220, 54
        bx = SCREEN_WIDTH // 2 - bw // 2
        if self.current_level + 1 < get_level_count():
            nxt = pygame.Rect(bx, 402, bw, bh)
            draw_plank_button(self.screen, nxt, PLANK_GREEN, PLANK_GREEN_DARK, WOOD_LIGHT, WOOD_BORDER,
                              "下一关", self.font_medium)
            self.buttons["next"] = nxt
            ry = 468
        else:
            ry = 420
        rst = pygame.Rect(bx, ry, bw, bh)
        draw_plank_button(self.screen, rst, PLANK_BLUE, PLANK_BLUE_DARK, WOOD_LIGHT, WOOD_BORDER,
                          "重玩本关", self.font_medium)
        self.buttons["restart_win"] = rst

        menu = pygame.Rect(bx, ry + 64, bw, bh)
        draw_plank_button(self.screen, menu, PANEL, PANEL_SHADE, WHITE, OUTLINE,
                          "返回菜单", self.font_medium, DARK)
        self.buttons["menu_win"] = menu

    def draw_mystery_win_overlay(self):
        """神秘关卡胜利面板：无星级、无分数"""
        self._dim(150)
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 210, 130, 420, 320)
        draw_plank_button(self.screen, panel, PANEL, PANEL_SHADE, WHITE, WOOD_BORDER)

        t = pygame.Rect(SCREEN_WIDTH // 2 - 150, 158, 300, 66)
        draw_plank_button(self.screen, t, PLANK_GREEN, PLANK_GREEN_DARK, WOOD_LIGHT, WOOD_BORDER)
        draw_text_outline(self.screen, "挑战成功!", self.font_large, WHITE,
                          (t.centerx, t.centery), width=3)

        draw_text_outline(self.screen, "全部箭头都成功飞出了棋盘", self.font_small,
                          DARK2, (SCREEN_WIDTH // 2, 272))

        bw, bh = 220, 54
        bx = SCREEN_WIDTH // 2 - bw // 2
        again = pygame.Rect(bx, 308, bw, bh)
        draw_plank_button(self.screen, again, PLANK_GREEN, PLANK_GREEN_DARK, WOOD_LIGHT, WOOD_BORDER,
                          "再来一局", self.font_medium)
        self.buttons["mystery_again"] = again

        menu = pygame.Rect(bx, 378, bw, bh)
        draw_plank_button(self.screen, menu, PANEL, PANEL_SHADE, WHITE, OUTLINE,
                          "返回菜单", self.font_medium, DARK)
        self.buttons["menu_win"] = menu

    def draw_lose_overlay(self):
        self._dim(150)
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 210, 160, 420, 300)
        draw_plank_button(self.screen, panel, PANEL, PANEL_SHADE, WHITE, WOOD_BORDER)

        t = pygame.Rect(SCREEN_WIDTH // 2 - 150, 192, 300, 66)
        draw_plank_button(self.screen, t, PLANK_RED, PLANK_RED_DARK, WOOD_LIGHT, WOOD_BORDER)
        draw_text_outline(self.screen, "游戏结束", self.font_large, WHITE, (t.centerx, t.centery), width=3)

        draw_text_outline(self.screen, "失误次数用完了，再试一次吧！", self.font_small,
                          DARK2, (SCREEN_WIDTH // 2, 300))

        bw, bh = 220, 54
        bx = SCREEN_WIDTH // 2 - bw // 2
        rst = pygame.Rect(bx, 330, bw, bh)
        draw_plank_button(self.screen, rst, PLANK_ORANGE, PLANK_ORANGE_DARK, WOOD_LIGHT, WOOD_BORDER,
                          "重新开始", self.font_medium)
        self.buttons["restart_lose"] = rst

        menu = pygame.Rect(bx, 394, bw, bh)
        draw_plank_button(self.screen, menu, PANEL, PANEL_SHADE, WHITE, OUTLINE,
                          "返回菜单", self.font_medium, DARK)
        self.buttons["menu_lose"] = menu

    def draw_all_clear_screen(self):
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 215, SCREEN_HEIGHT // 2 - 170, 430, 340)
        draw_plank_button(self.screen, panel, PANEL, PANEL_SHADE, WHITE, WOOD_BORDER)

        t = pygame.Rect(SCREEN_WIDTH // 2 - 160, panel.y + 30, 320, 70)
        draw_plank_button(self.screen, t, PLANK_GREEN, PLANK_GREEN_DARK, WOOD_LIGHT, WOOD_BORDER)
        draw_text_outline(self.screen, "全部通关!", self.font_title, WHITE, (t.centerx, t.centery), width=3)

        draw_text_outline(self.screen, "恭喜你完成了所有关卡，你太棒啦！", self.font_medium, DARK2,
                          (SCREEN_WIDTH // 2, panel.y + 155))

        # 三颗金星庆祝
        for i in range(3):
            self.draw_star(SCREEN_WIDTH // 2 - 80 + i * 80, panel.y + 215, 24, STAR_GOLD, shine=True)

        btn = pygame.Rect(SCREEN_WIDTH // 2 - 120, panel.y + 260, 240, 58)
        draw_plank_button(self.screen, btn, PLANK_BLUE, PLANK_BLUE_DARK, WOOD_LIGHT, WOOD_BORDER,
                          "返回主菜单", self.font_medium)
        self.buttons["menu"] = btn

    def draw_star(self, cx, cy, radius, color, filled=True, shine=False):
        """五角星（2x 超采样离屏绘制，边缘细腻）"""
        S = SS
        box = radius * 2 + 8
        big = pygame.Surface((box * S, box * S), pygame.SRCALPHA)
        bc = box * S // 2
        pts = []
        for i in range(10):
            ang = math.pi / 2 + i * math.pi / 5
            rr = radius * S if i % 2 == 0 else radius * 0.42 * S
            pts.append((bc + rr * math.cos(ang), bc - rr * math.sin(ang)))
        if filled:
            pygame.draw.polygon(big, color, pts)
            pygame.draw.polygon(big, OUTLINE, pts, 2 * S)
            if shine and color == STAR_GOLD:
                pygame.draw.circle(big, (255, 244, 200),
                                   (int(bc - radius * 0.28 * S), int(bc - radius * 0.32 * S)),
                                   max(2, int(radius * 0.2 * S)))
        else:
            pygame.draw.polygon(big, color, pts, 2 * S)
        small = pygame.transform.smoothscale(big, (box, box))
        self.screen.blit(small, (int(cx - box // 2), int(cy - box // 2)))
