from pico2d import get_time, load_image

import camera

# 4-frame idle sheet inside farm_merchant_idle.png (left, bottom, width, height)
FRAMES = (
    (0, 0, 161, 230),
    (169, 0, 156, 230),
    (331, 0, 154, 230),
    (493, 0, 156, 230),
)
FRAME_DURATION = 0.25
DRAW_HEIGHT = 90


class FarmMerchant:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.frame_timer = 0.0
        self.last_update_time = get_time()
        if FarmMerchant.image is None:
            FarmMerchant.image = load_image("assets/npc/farm_merchant_idle.png")
        self.image = FarmMerchant.image

    def update(self):
        current_time = get_time()
        delta_time = max(0.0, current_time - self.last_update_time)
        self.last_update_time = current_time
        self.frame_timer += delta_time
        while self.frame_timer >= FRAME_DURATION:
            self.frame = (self.frame + 1) % len(FRAMES)
            self.frame_timer -= FRAME_DURATION

    def draw(self):
        left, bottom, width, height = FRAMES[self.frame]
        self.image.clip_composite_draw(
            left,
            bottom,
            width,
            height,
            0,
            "",
            self.x - camera.x,
            self.y - camera.y,
            width * DRAW_HEIGHT / height,
            DRAW_HEIGHT,
        )
