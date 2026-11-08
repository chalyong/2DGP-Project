from pico2d import load_image

import camera


class MineEntrance:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        if MineEntrance.image is None:
            MineEntrance.image = load_image(
                "assets/buildings/mine_wood_support_entrance.png"
            )

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x - camera.x, self.y - camera.y)
