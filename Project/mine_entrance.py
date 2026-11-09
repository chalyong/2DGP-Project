from pico2d import load_image

import camera


class MineEntrance:
    image = None

    def __init__(self, x, y, ore_path):
        self.x = x
        self.y = y
        if MineEntrance.image is None:
            MineEntrance.image = load_image(
                "assets/buildings/mine_wood_support_entrance.png"
            )
        self.ore_image = load_image(ore_path)

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x - camera.x, self.y - camera.y)
        self.ore_image.draw(
                    self.x - camera.x,
                    self.y + 60 - camera.y,
                )