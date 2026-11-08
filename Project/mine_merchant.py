from pico2d import load_image

import camera


class MineMerchant:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.frame_timer = 0
        if MineMerchant.image is None:
            MineMerchant.image = load_image(
                "assets/npc/mine_merchant_idle.png"
            )

    def update(self):
        self.frame_timer += 1
        if self.frame_timer >= 12:
            self.frame = (self.frame + 1) % 4
            self.frame_timer = 0

    def draw(self):
        self.image.clip_composite_draw(
            self.frame * 64,
            0,
            64,
            64,
            0,
            "",
            self.x - camera.x,
            self.y - camera.y,
            56,
            64,
        )
