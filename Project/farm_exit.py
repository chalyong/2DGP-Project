from pico2d import load_image

import camera

DRAW_WIDTH = 300
DRAW_HEIGHT = 158


class FarmExit:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        if FarmExit.image is None:
            FarmExit.image = load_image("assets/buildings/farm_exit.png")
        self.image = FarmExit.image

    def update(self):
        pass

    def draw(self):
        self.image.draw(
            self.x - camera.x,
            self.y - camera.y,
            DRAW_WIDTH,
            DRAW_HEIGHT,
        )
