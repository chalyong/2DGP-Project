SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WORLD_WIDTH = 1600
WORLD_HEIGHT = 600

x = 0
y = 0


def reset():
    global x, y
    x = 0
    y = 0


def follow(target_x):
    global x
    max_x = WORLD_WIDTH - SCREEN_WIDTH
    x = max(0, min(target_x - SCREEN_WIDTH // 2, max_x))
