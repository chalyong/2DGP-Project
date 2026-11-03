from pico2d import load_image

import camera


class Background:
    image = None

    def __init__(self):
        if Background.image is None:
            Background.image = load_image("assets/background/world_background.png")
        self.image = Background.image

    def update(self):
        pass

    def draw(self):
        self.image.draw(
            camera.WORLD_WIDTH // 2 - camera.x,
            camera.WORLD_HEIGHT // 2 - camera.y,
            camera.WORLD_WIDTH,
            camera.WORLD_HEIGHT,
        )
