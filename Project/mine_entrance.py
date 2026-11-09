from pico2d import load_image

import camera


class MineEntrance:
    image = None
    locked_image = None

    def __init__(self, x, y, ore_path, locked=False):
        self.x = x
        self.y = y
        self.locked = locked
        if MineEntrance.image is None:
            MineEntrance.image = load_image(
                "assets/buildings/mine_wood_support_entrance.png"
            )
        if MineEntrance.locked_image is None:
            MineEntrance.locked_image = load_image(
                "assets/buildings/mine_locked_x.png"
            )
        self.ore_image = load_image(ore_path)

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x - camera.x, self.y - camera.y)
        if self.locked:
            self.locked_image.draw(
                self.x - camera.x,
                self.y - camera.y - 10,
                80, 80
            )
        self.ore_image.draw(
                    self.x - camera.x,
                    self.y + 60 - camera.y,
                )