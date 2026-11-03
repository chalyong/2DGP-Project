from pico2d import load_image

import camera


class Background:
    def __init__(self):
        self.image = load_image("assets/background/world_background.png")

    def update(self):
        pass

    def draw(self):
        self.image.draw(
            camera.WORLD_WIDTH // 2 - camera.x,
            camera.WORLD_HEIGHT // 2 - camera.y,
            camera.WORLD_WIDTH,
            camera.WORLD_HEIGHT,
        )
