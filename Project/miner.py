from pico2d import get_time, load_image

import camera

# frames inside mine_miner_mining.png (left, bottom, width, height)
FRAMES = (
    (69, 0, 214, 660),
    (370, 0, 226, 660),
    (684, 0, 223, 660),
    (981, 0, 315, 660),
    (1296, 0, 256, 660),
    (1624, 0, 258, 660),
    (1941, 0, 225, 660),
)
CYCLE_SECONDS = 2.0
FRAME_DURATION = CYCLE_SECONDS / len(FRAMES)
REF_HEIGHT = 588
DRAW_HEIGHT_SCALE = 1.3
DRAW_HEIGHT = 96 * DRAW_HEIGHT_SCALE


class Miner:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.frame_timer = 0.0
        self.last_update_time = get_time()
        if Miner.image is None:
            Miner.image = load_image("assets/npc/mine_miner_mining.png")
        self.image = Miner.image

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
        scale = DRAW_HEIGHT / REF_HEIGHT
        draw_width = width * scale
        draw_height = height * scale
        # keep feet on the same ground line for every frame
        py = self.y + (draw_height - DRAW_HEIGHT) / 2
        self.image.clip_composite_draw(
            left,
            bottom,
            width,
            height,
            0,
            "",
            self.x - camera.x,
            py - camera.y,
            draw_width,
            draw_height,
        )
