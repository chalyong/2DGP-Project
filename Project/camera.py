SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PIXELS_PER_METER = 40
METERS_PER_PIXEL = 1 / PIXELS_PER_METER
WORLD_WIDTH_METERS = 40
WORLD_HEIGHT_METERS = 15
DEFAULT_WORLD_WIDTH = int(WORLD_WIDTH_METERS * PIXELS_PER_METER)
DEFAULT_WORLD_HEIGHT = int(WORLD_HEIGHT_METERS * PIXELS_PER_METER)
WORLD_WIDTH = DEFAULT_WORLD_WIDTH
WORLD_HEIGHT = DEFAULT_WORLD_HEIGHT

x = 0
y = 0


def set_world(width, height):
    global WORLD_WIDTH, WORLD_HEIGHT
    WORLD_WIDTH = width
    WORLD_HEIGHT = height


def restore_world():
    set_world(DEFAULT_WORLD_WIDTH, DEFAULT_WORLD_HEIGHT)


def reset():
    global x, y
    x = 0
    y = 0


def follow(target_x):
    global x
    max_x = WORLD_WIDTH - SCREEN_WIDTH
    x = max(0, min(target_x - SCREEN_WIDTH // 2, max_x))


def follow_2d(target_x, target_y):
    global x, y
    max_x = max(0, WORLD_WIDTH - SCREEN_WIDTH)
    max_y = max(0, WORLD_HEIGHT - SCREEN_HEIGHT)
    x = max(0, min(target_x - SCREEN_WIDTH // 2, max_x))
    y = max(0, min(target_y - SCREEN_HEIGHT // 2, max_y))
