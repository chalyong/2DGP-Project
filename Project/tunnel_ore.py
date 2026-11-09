from pico2d import load_image

import camera


class TunnelOre:
    def __init__(self, x, y, image_path):
        self.x = x
        self.y = y
        self.image = load_image(image_path)

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x - camera.x, self.y - camera.y, 200, 200)
