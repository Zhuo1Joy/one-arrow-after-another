# 一箭又一箭小游戏

## 项目简介

"一箭又一箭"是一款基于 Python 和 Pygame 开发的休闲解谜游戏。玩家需要观察箭头的方向和相互阻挡关系，按照合适的顺序点击箭头，使所有箭头依次飞出棋盘。

### 游戏规则

- 棋盘中包含若干带方向的箭头，箭头方向分为上、下、左、右四种
- 玩家点击某个箭头后，程序检查该箭头前进方向上的路径
- 如果箭头与棋盘边界之间没有其他箭头阻挡，该箭头飞出棋盘并被消除
- 如果路径上存在其他箭头，该箭头不能被消除，并消耗一次失误机会
- 清除本关全部箭头后即可进入下一关
- 失误次数耗尽时，本关失败，可重新开始

## 开发环境

- Python 3.10+
- Pygame 2.5.0+
- 操作系统：Windows / macOS / Linux

## 安装和运行

### 1. 克隆项目

```bash
git clone <repository-url>
cd one-arrow-after-another
```

### 2. 创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行游戏

```bash
python -m game.main
```

## 游戏操作说明

### 开始界面
- 点击"开始游戏"按钮进入关卡选择界面

### 关卡选择界面
- 点击关卡卡片（1/2/3）选择对应关卡
- 点击"返回"按钮返回主菜单
- 问号卡片为神秘关卡（功能开发中）

### 游戏界面
- **点击箭头**：尝试让箭头飞出棋盘
- **菜单按钮**：返回关卡选择界面
- **重新开始按钮**：重置当前关卡
- **撤销按钮**：撤销上一步操作（每关限1次）

### 界面说明
- **关卡**：显示当前关卡编号
- **剩余**：显示剩余箭头数量
- **失误**：显示剩余失误次数（默认3次）

## 功能特性

### 基础功能
- ✅ 图形化游戏界面（开始界面、游戏界面、通关/失败界面）
- ✅ 四种方向的箭头（上、下、左、右）
- ✅ 鼠标点击选择箭头
- ✅ 路径检测算法（判断箭头前方是否有阻挡）
- ✅ 箭头飞出动画效果
- ✅ 碰撞反馈动画（晃动效果）
- ✅ 失误次数管理
- ✅ 3个精心设计的关卡
- ✅ 通关和失败判定
- ✅ 重新开始功能

### 扩展功能
- ✅ 关卡选择界面
- ✅ 撤销上一步功能（每关1次）
- ✅ 神秘关卡卡片（预留功能）
- ✅ 中文字体支持

## 项目结构

```
one-arrow-after-another/
├── game/
│   ├── __init__.py      # 模块初始化
│   ├── main.py          # 游戏入口
│   ├── settings.py      # 游戏配置常量
│   ├── arrow.py         # 箭头类
│   ├── board.py         # 棋盘类
│   ├── game.py          # 游戏主逻辑
│   └── levels.py        # 关卡数据
├── assets/              # 资源文件目录
├── tests/               # 测试文件目录
├── venv/                # Python 虚拟环境
├── requirements.txt     # 项目依赖
└── README.md           # 项目说明文档
```

## 核心算法

### 路径检测算法

```python
def check_path_clear(self, arrow):
    """检查箭头前方是否有阻挡"""
    row, col = arrow.row, arrow.col
    direction = arrow.direction
    
    if direction == 'right':
        for c in range(col + 1, self.cols):
            if self.has_arrow(row, c):
                return False
    elif direction == 'left':
        for c in range(col - 1, -1, -1):
            if self.has_arrow(row, c):
                return False
    elif direction == 'down':
        for r in range(row + 1, self.rows):
            if self.has_arrow(r, col):
                return False
    elif direction == 'up':
        for r in range(row - 1, -1, -1):
            if self.has_arrow(r, col):
                return False
    
    return True
```

## 技术栈

- **编程语言**：Python 3.10+
- **图形库**：Pygame 2.5.0+
- **AIGC 工具**：Trae（代码生成、关卡设计、动画实现）

## 开发说明

本项目使用 AIGC 工具辅助开发，主要借助 Trae 完成：
- 游戏框架和核心逻辑
- 路径检测算法
- 关卡数据设计
- 动画效果实现
- Bug 调试和修复

## 许可证

本项目为课程作业项目，仅供学习参考使用。

## 联系方式

如有问题或建议，请通过 GitHub Issues 反馈。
