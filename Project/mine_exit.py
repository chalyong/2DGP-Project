from pico2d import load_image

import camera


class MineExit:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        if MineExit.image is None:
            MineExit.image = load_image("assets/buildings/mine_exit.png")

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x - camera.x, self.y - camera.y)
