"""游戏主逻辑"""
import pygame
import copy
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BG_COLOR, WHITE, BLACK, GRAY, RED, GREEN, BLUE,
    MAX_MISTAKES, STATE_START, STATE_LEVEL_SELECT, STATE_PLAYING, STATE_WIN, STATE_LOSE, STATE_ALL_CLEAR,
    BOARD_ROWS, BOARD_COLS, CELL_SIZE, get_font_path, YELLOW
)
from game.board import Board
from game.levels import get_level_copy, get_level_count


class Game:
    """游戏主类"""

    def __init__(self):
        """初始化游戏"""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("一箭又一箭")
        self.clock = pygame.time.Clock()

        # 字体 - 使用中文字体
        font_path = get_font_path()
        self.font_large = pygame.font.Font(font_path, 60)
        self.font_medium = pygame.font.Font(font_path, 36)
        self.font_small = pygame.font.Font(font_path, 24)

        # 游戏状态
        self.state = STATE_START
        self.current_level = 0
        self.mistakes_left = MAX_MISTAKES
        self.board = Board()

        # 撤销功能
        self.undo_available = True  # 每关可使用1次撤销
        self.undo_history = None  # 保存上一步状态

        # 计算棋盘位置（居中）
        board_width = BOARD_COLS * CELL_SIZE
        board_height = BOARD_ROWS * CELL_SIZE
        self.board_x = (SCREEN_WIDTH - board_width) // 2
        self.board_y = (SCREEN_HEIGHT - board_height) // 2 + 30

        # 按钮区域
        self.buttons = {}

    def start(self):
        """开始游戏主循环"""
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0  # 转换为秒

            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)

            # 更新
            self.update(dt)

            # 绘制
            self.draw()

        pygame.quit()

    def save_state(self):
        """保存当前状态用于撤销"""
        if self.undo_available:
            self.undo_history = {
                'arrows': copy.deepcopy(self.board.arrows),
                'mistakes_left': self.mistakes_left
            }

    def undo(self):
        """撤销上一步"""
        if self.undo_available and self.undo_history:
            self.board.arrows = copy.deepcopy(self.undo_history['arrows'])
            self.mistakes_left = self.undo_history['mistakes_left']
            self.undo_available = False
            self.undo_history = None

    def handle_click(self, pos):
        """处理鼠标点击"""
        x, y = pos

        if self.state == STATE_START:
            # 检查开始按钮
            if "start" in self.buttons:
                btn_rect = self.buttons["start"]
                if btn_rect.collidepoint(x, y):
                    self.state = STATE_LEVEL_SELECT

        elif self.state == STATE_LEVEL_SELECT:
            # 检查关卡选择
            for i in range(3):
                key = f"level_{i}"
                if key in self.buttons:
                    btn_rect = self.buttons[key]
                    if btn_rect.collidepoint(x, y):
                        self.current_level = i
                        self.load_level()
                        return
            # 检查神秘关卡
            if "mystery" in self.buttons:
                btn_rect = self.buttons["mystery"]
                if btn_rect.collidepoint(x, y):
                    pass  # 功能暂时留空
            # 检查返回按钮
            if "back" in self.buttons:
                btn_rect = self.buttons["back"]
                if btn_rect.collidepoint(x, y):
                    self.state = STATE_START

        elif self.state == STATE_PLAYING:
            # 检查重新开始按钮
            if "restart" in self.buttons:
                btn_rect = self.buttons["restart"]
                if btn_rect.collidepoint(x, y):
                    self.restart_level()
                    return

            # 检查撤销按钮
            if "undo" in self.buttons:
                btn_rect = self.buttons["undo"]
                if btn_rect.collidepoint(x, y) and self.undo_available and self.undo_history:
                    self.undo()
                    return

            # 检查返回按钮
            if "back_to_menu" in self.buttons:
                btn_rect = self.buttons["back_to_menu"]
                if btn_rect.collidepoint(x, y):
                    self.state = STATE_LEVEL_SELECT
                    return

            # 检查箭头点击
            arrow = self.board.get_arrow_at(x, y, self.board_x, self.board_y)
            if arrow:
                self.try_remove_arrow(arrow)

        elif self.state == STATE_WIN:
            # 检查下一关按钮
            if "next" in self.buttons:
                btn_rect = self.buttons["next"]
                if btn_rect.collidepoint(x, y):
                    self.next_level()

            # 检查重新开始按钮
            if "restart_win" in self.buttons:
                btn_rect = self.buttons["restart_win"]
                if btn_rect.collidepoint(x, y):
                    self.restart_level()

        elif self.state == STATE_LOSE:
            # 检查重新开始按钮
            if "restart_lose" in self.buttons:
                btn_rect = self.buttons["restart_lose"]
                if btn_rect.collidepoint(x, y):
                    self.restart_level()

        elif self.state == STATE_ALL_CLEAR:
            # 检查返回主菜单按钮
            if "menu" in self.buttons:
                btn_rect = self.buttons["menu"]
                if btn_rect.collidepoint(x, y):
                    self.state = STATE_LEVEL_SELECT

    def start_game(self):
        """开始新游戏"""
        self.current_level = 0
        self.load_level()

    def load_level(self):
        """加载当前关卡"""
        level_data = get_level_copy(self.current_level)
        if level_data:
            self.board.load_level(level_data)
            self.mistakes_left = MAX_MISTAKES
            self.undo_available = True
            self.undo_history = None
            self.state = STATE_PLAYING
        else:
            self.state = STATE_ALL_CLEAR

    def restart_level(self):
        """重新开始当前关卡"""
        self.load_level()

    def next_level(self):
        """进入下一关"""
        self.current_level += 1
        self.load_level()

    def try_remove_arrow(self, arrow):
        """尝试移除箭头"""
        # 保存状态用于撤销
        self.save_state()

        if self.board.check_path_clear(arrow):
            # 路径畅通，箭头飞出
            arrow.start_fly()
        else:
            # 路径被阻挡，晃动并扣失误
            arrow.start_shake()
            self.mistakes_left -= 1
            if self.mistakes_left <= 0:
                self.state = STATE_LOSE

    def update(self, dt):
        """更新游戏状态"""
        if self.state == STATE_PLAYING:
            self.board.update(dt)

            # 检查是否通关
            if self.board.is_cleared():
                # 检查是否还有下一关
                if self.current_level + 1 < get_level_count():
                    self.state = STATE_WIN
                else:
                    self.state = STATE_ALL_CLEAR

    def draw(self):
        """绘制游戏画面"""
        self.screen.fill(BG_COLOR)
        self.buttons = {}

        if self.state == STATE_START:
            self.draw_start_screen()
        elif self.state == STATE_LEVEL_SELECT:
            self.draw_level_select_screen()
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
        """绘制开始界面"""
        # 标题
        title = self.font_large.render("一箭又一箭", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title, title_rect)

        # 说明
        desc = self.font_small.render("点击箭头使其飞出棋盘", True, GRAY)
        desc_rect = desc.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(desc, desc_rect)

        # 开始按钮
        btn_width, btn_height = 200, 60
        btn_x = (SCREEN_WIDTH - btn_width) // 2
        btn_y = SCREEN_HEIGHT // 2 + 40
        btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
        pygame.draw.rect(self.screen, GREEN, btn_rect, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, btn_rect, 3, border_radius=10)

        btn_text = self.font_medium.render("开始游戏", True, WHITE)
        text_rect = btn_text.get_rect(center=btn_rect.center)
        self.screen.blit(btn_text, text_rect)

        self.buttons["start"] = btn_rect

    def draw_level_select_screen(self):
        """绘制关卡选择界面"""
        # 标题
        title = self.font_large.render("选择关卡", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        # 关卡卡片
        card_width, card_height = 150, 150
        card_spacing = 30
        total_width = 4 * card_width + 3 * card_spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        card_y = SCREEN_HEIGHT // 2 - card_height // 2

        # 关卡1
        card1_rect = pygame.Rect(start_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, GREEN, card1_rect, border_radius=15)
        pygame.draw.rect(self.screen, BLACK, card1_rect, 3, border_radius=15)
        text1 = self.font_medium.render("关卡 1", True, WHITE)
        text1_rect = text1.get_rect(center=card1_rect.center)
        self.screen.blit(text1, text1_rect)
        self.buttons["level_0"] = card1_rect

        # 关卡2
        card2_x = start_x + card_width + card_spacing
        card2_rect = pygame.Rect(card2_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, BLUE, card2_rect, border_radius=15)
        pygame.draw.rect(self.screen, BLACK, card2_rect, 3, border_radius=15)
        text2 = self.font_medium.render("关卡 2", True, WHITE)
        text2_rect = text2.get_rect(center=card2_rect.center)
        self.screen.blit(text2, text2_rect)
        self.buttons["level_1"] = card2_rect

        # 关卡3
        card3_x = start_x + 2 * (card_width + card_spacing)
        card3_rect = pygame.Rect(card3_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, RED, card3_rect, border_radius=15)
        pygame.draw.rect(self.screen, BLACK, card3_rect, 3, border_radius=15)
        text3 = self.font_medium.render("关卡 3", True, WHITE)
        text3_rect = text3.get_rect(center=card3_rect.center)
        self.screen.blit(text3, text3_rect)
        self.buttons["level_2"] = card3_rect

        # 神秘关卡（问号）
        card4_x = start_x + 3 * (card_width + card_spacing)
        card4_rect = pygame.Rect(card4_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, GRAY, card4_rect, border_radius=15)
        pygame.draw.rect(self.screen, BLACK, card4_rect, 3, border_radius=15)
        text4 = self.font_large.render("?", True, WHITE)
        text4_rect = text4.get_rect(center=card4_rect.center)
        self.screen.blit(text4, text4_rect)
        self.buttons["mystery"] = card4_rect

        # 返回按钮
        btn_width, btn_height = 150, 50
        btn_x = (SCREEN_WIDTH - btn_width) // 2
        btn_y = SCREEN_HEIGHT - 100
        btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
        pygame.draw.rect(self.screen, GRAY, btn_rect, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, btn_rect, 2, border_radius=10)
        btn_text = self.font_medium.render("返回", True, WHITE)
        btn_text_rect = btn_text.get_rect(center=btn_rect.center)
        self.screen.blit(btn_text, btn_text_rect)
        self.buttons["back"] = btn_rect

    def draw_game_screen(self):
        """绘制游戏界面"""
        # 顶部信息栏
        info_y = 20

        # 返回菜单按钮（左上角）
        back_btn_width, back_btn_height = 80, 35
        back_btn_x = 20
        back_btn_y = 20
        back_rect = pygame.Rect(back_btn_x, back_btn_y, back_btn_width, back_btn_height)
        pygame.draw.rect(self.screen, GRAY, back_rect, border_radius=6)
        pygame.draw.rect(self.screen, BLACK, back_rect, 2, border_radius=6)
        back_text = self.font_small.render("菜单", True, WHITE)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)
        self.buttons["back_to_menu"] = back_rect

        # 关卡信息
        level_text = self.font_small.render(f"关卡: {self.current_level + 1}", True, BLACK)
        self.screen.blit(level_text, (130, info_y + 5))

        # 剩余箭头
        arrows_text = self.font_small.render(f"剩余: {self.board.get_remaining_count()}", True, BLACK)
        self.screen.blit(arrows_text, (SCREEN_WIDTH // 2 - arrows_text.get_width() // 2, info_y + 5))

        # 剩余失误次数
        mistakes_text = self.font_small.render(f"失误: {self.mistakes_left}", True, RED)
        self.screen.blit(mistakes_text, (SCREEN_WIDTH - mistakes_text.get_width() - 30, info_y + 5))

        # 绘制棋盘
        self.board.draw(self.screen, self.board_x, self.board_y)

        # 按钮区域
        btn_y = self.board_y + BOARD_ROWS * CELL_SIZE + 30
        btn_width, btn_height = 120, 45

        # 重新开始按钮
        restart_x = SCREEN_WIDTH // 2 - btn_width - 20
        restart_rect = pygame.Rect(restart_x, btn_y, btn_width, btn_height)
        pygame.draw.rect(self.screen, BLUE, restart_rect, border_radius=8)
        pygame.draw.rect(self.screen, BLACK, restart_rect, 2, border_radius=8)
        restart_text = self.font_small.render("重新开始", True, WHITE)
        restart_text_rect = restart_text.get_rect(center=restart_rect.center)
        self.screen.blit(restart_text, restart_text_rect)
        self.buttons["restart"] = restart_rect

        # 撤销按钮
        undo_x = SCREEN_WIDTH // 2 + 20
        undo_rect = pygame.Rect(undo_x, btn_y, btn_width, btn_height)

        # 根据撤销可用状态改变颜色
        if self.undo_available and self.undo_history:
            undo_color = YELLOW
        else:
            undo_color = GRAY

        pygame.draw.rect(self.screen, undo_color, undo_rect, border_radius=8)
        pygame.draw.rect(self.screen, BLACK, undo_rect, 2, border_radius=8)
        undo_text = self.font_small.render("撤销(1次)", True, BLACK if undo_color == YELLOW else WHITE)
        undo_text_rect = undo_text.get_rect(center=undo_rect.center)
        self.screen.blit(undo_text, undo_text_rect)
        self.buttons["undo"] = undo_rect

    def draw_win_overlay(self):
        """绘制通关覆盖层"""
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(WHITE)
        self.screen.blit(overlay, (0, 0))

        # 通关文字
        win_text = self.font_large.render("恭喜通关!", True, GREEN)
        text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(win_text, text_rect)

        # 下一关按钮
        btn_width, btn_height = 200, 60
        btn_x = (SCREEN_WIDTH - btn_width) // 2
        btn_y = SCREEN_HEIGHT // 2
        btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
        pygame.draw.rect(self.screen, GREEN, btn_rect, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, btn_rect, 3, border_radius=10)

        btn_text = self.font_medium.render("下一关", True, WHITE)
        text_rect = btn_text.get_rect(center=btn_rect.center)
        self.screen.blit(btn_text, text_rect)

        self.buttons["next"] = btn_rect

        # 重新开始按钮
        btn2_y = btn_y + 80
        btn2_rect = pygame.Rect(btn_x, btn2_y, btn_width, btn_height)
        pygame.draw.rect(self.screen, BLUE, btn2_rect, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, btn2_rect, 3, border_radius=10)

        btn2_text = self.font_medium.render("重玩本关", True, WHITE)
        text2_rect = btn2_text.get_rect(center=btn2_rect.center)
        self.screen.blit(btn2_text, text2_rect)

        self.buttons["restart_win"] = btn2_rect

    def draw_lose_overlay(self):
        """绘制失败覆盖层"""
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(WHITE)
        self.screen.blit(overlay, (0, 0))

        # 失败文字
        lose_text = self.font_large.render("游戏结束", True, RED)
        text_rect = lose_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(lose_text, text_rect)

        # 重新开始按钮
        btn_width, btn_height = 200, 60
        btn_x = (SCREEN_WIDTH - btn_width) // 2
        btn_y = SCREEN_HEIGHT // 2
        btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
        pygame.draw.rect(self.screen, RED, btn_rect, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, btn_rect, 3, border_radius=10)

        btn_text = self.font_medium.render("重新开始", True, WHITE)
        text_rect = btn_text.get_rect(center=btn_rect.center)
        self.screen.blit(btn_text, text_rect)

        self.buttons["restart_lose"] = btn_rect

    def draw_all_clear_screen(self):
        """绘制全部通关界面"""
        # 祝贺文字
        title = self.font_large.render("全部通关!", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title, title_rect)

        # 说明
        desc = self.font_medium.render("恭喜你完成了所有关卡!", True, BLACK)
        desc_rect = desc.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(desc, desc_rect)

        # 返回主菜单按钮
        btn_width, btn_height = 220, 60
        btn_x = (SCREEN_WIDTH - btn_width) // 2
        btn_y = SCREEN_HEIGHT // 2 + 30
        btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
        pygame.draw.rect(self.screen, BLUE, btn_rect, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, btn_rect, 3, border_radius=10)

        btn_text = self.font_medium.render("返回主菜单", True, WHITE)
        text_rect = btn_text.get_rect(center=btn_rect.center)
        self.screen.blit(btn_text, text_rect)

        self.buttons["menu"] = btn_rect
