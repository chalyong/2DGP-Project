from pico2d import load_image

import camera


class Building:
    def __init__(self, image_path, x, y=325):
        self.image = load_image(image_path)
        self.x = x
        self.y = y

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x - camera.x, self.y - camera.y)
