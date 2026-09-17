"""游戏入口"""
import os
import sys

# 保证直接以脚本方式运行（python game/main.py）时也能找到 game 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game import Game


def main():
    """主函数"""
    game = Game()
    game.start()


if __name__ == "__main__":
    main()
