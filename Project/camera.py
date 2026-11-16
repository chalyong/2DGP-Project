SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PIXELS_PER_METER = 40
METERS_PER_PIXEL = 1 / PIXELS_PER_METER
WORLD_WIDTH_METERS = 40
WORLD_HEIGHT_METERS = 15
WORLD_WIDTH = int(WORLD_WIDTH_METERS * PIXELS_PER_METER)
WORLD_HEIGHT = int(WORLD_HEIGHT_METERS * PIXELS_PER_METER)

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
