from pico2d import load_image

import camera

# one figure inside mine_miner_mining.png (left, bottom, width, height)
SOURCE_RECT = (69, 65, 214, 588)
DRAW_HEIGHT_SCALE = 1.3
DRAW_HEIGHT = 96 * DRAW_HEIGHT_SCALE


class Miner:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        if Miner.image is None:
            Miner.image = load_image("assets/npc/mine_miner_mining.png")
        self.image = Miner.image

    def update(self):
        pass

    def draw(self):
        left, bottom, width, height = SOURCE_RECT
        self.image.clip_composite_draw(
            left,
            bottom,
            width,
            height,
            0,
            "",
            self.x - camera.x,
            self.y - camera.y,
            width * DRAW_HEIGHT / height,
            DRAW_HEIGHT,
        )
