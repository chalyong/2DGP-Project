from pico2d import load_image

import camera


class TunnelExit:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        if TunnelExit.image is None:
            TunnelExit.image = load_image("assets/buildings/tunnel_exit.png")

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x - camera.x, self.y - camera.y)
