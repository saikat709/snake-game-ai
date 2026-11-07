"""
Game configuration and visual theme constants.
Cyberpunk / Neon Retrowave Aesthetic.
"""

# Directions
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)

# Screen & Display Settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TARGET_FPS = 60

# Arena / Grid Dimensions
GRID_COLS = 28
GRID_ROWS = 22
CELL_SIZE = 26

# Calculated Arena Dimensions
ARENA_WIDTH = GRID_COLS * CELL_SIZE   # 728 px
ARENA_HEIGHT = GRID_ROWS * CELL_SIZE  # 572 px

# Centering Arena on Screen with Top HUD
ARENA_X = (SCREEN_WIDTH - ARENA_WIDTH) // 2       # 148 px
ARENA_Y = 110                                    # Top offset below HUD (110 to 682 px)

# Snake Speed & Gameplay
INITIAL_SNAKE_SPEED = 9.0    # Ticks per second
MAX_SNAKE_SPEED = 18.0       # Ticks per second
SPEED_INCREMENT = 0.25       # Speed increase per food eaten
COMBO_TIMEOUT = 3.8          # Seconds before combo resets

# Color Palette (RGB)
COLOR_BG_DARK = (8, 10, 18)
COLOR_BG_LIGHT = (14, 18, 32)
COLOR_GRID_LINE = (18, 25, 45)
COLOR_GRID_DOT = (35, 52, 90)
COLOR_ARENA_BORDER = (0, 240, 255)
COLOR_ARENA_BORDER_GLOW = (0, 150, 220)

# Snake Colors
COLOR_SNAKE_HEAD = (0, 245, 255)       # Electric Cyan
COLOR_SNAKE_BODY_START = (0, 230, 255) # Bright Cyan
COLOR_SNAKE_BODY_MID = (0, 255, 170)   # Neon Teal / Emerald
COLOR_SNAKE_BODY_END = (168, 85, 247)  # Cyber Violet
COLOR_SNAKE_EYE = (255, 255, 255)
COLOR_SNAKE_PUPIL = (10, 15, 30)

# Food Colors
COLOR_FOOD_NORMAL = (255, 45, 85)      # Neon Crimson / Pink
COLOR_FOOD_NORMAL_GLOW = (255, 20, 100)
COLOR_FOOD_BONUS = (255, 215, 0)       # Quantum Gold
COLOR_FOOD_BONUS_GLOW = (255, 180, 0)

# UI Accent Colors
COLOR_WHITE = (245, 248, 255)
COLOR_TEXT_DIM = (120, 140, 175)
COLOR_CYAN = (0, 240, 255)
COLOR_GOLD = (255, 210, 30)
COLOR_MAGENTA = (255, 40, 150)
COLOR_PANEL_BG = (12, 16, 28, 220)
COLOR_PANEL_BORDER = (35, 55, 95)
