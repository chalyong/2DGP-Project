from pico2d import load_image

import camera


class Background:
    image = None
    mine_image = None
    tunnel_image = None

    def __init__(self):
        if Background.image is None:
            Background.image = load_image("assets/background/world_background.png")
        if Background.mine_image is None:
            Background.mine_image = load_image("assets/background/mine_background.png")
        if Background.tunnel_image is None:
            Background.tunnel_image = load_image(
                "assets/background/tunnel_interior.png"
            )
        self.image = Background.image

    def use_mine_map(self):
        self.image = Background.mine_image

    def use_tunnel_map(self):
        self.image = Background.tunnel_image

    def update(self):
        pass

    def draw(self):
        self.image.draw(
            camera.WORLD_WIDTH // 2 - camera.x,
            camera.WORLD_HEIGHT // 2 - camera.y,
            camera.WORLD_WIDTH,
            camera.WORLD_HEIGHT,
        )
