from pico2d import get_time, load_font, load_image

import camera
import game_state

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
    font = None

    def __init__(self, x, y, ore_name):
        self.x = x
        self.y = y
        self.ore_name = ore_name
        self.frame = 0
        self.frame_timer = 0.0
        self.last_update_time = get_time()
        self.notification = None
        self.notification_started = 0
        if Miner.image is None:
            Miner.image = load_image("assets/npc/mine_miner_mining.png")
        if Miner.font is None:
            Miner.font = load_font(r"C:\Windows\Fonts\consolab.ttf", 10)
        self.image = Miner.image

    def update(self):
        current_time = get_time()
        delta_time = max(0.0, current_time - self.last_update_time)
        self.last_update_time = current_time
        self.frame_timer += delta_time
        while self.frame_timer >= FRAME_DURATION:
            self.frame = (self.frame + 1) % len(FRAMES)
            self.frame_timer -= FRAME_DURATION
            if self.frame == 0:
                game_state.collected_items[self.ore_name] += 1
                self.notification = f"{self.ore_name.upper()} * 1"
                self.notification_started = current_time

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
        self._draw_notification()

    def _draw_notification(self):
        if not self.notification:
            return
        elapsed = get_time() - self.notification_started
        duration = 1.0
        if elapsed >= duration:
            self.notification = None
            return
        progress = elapsed / duration
        rise = 18 * progress
        start_color = (255, 239, 177)
        end_color = (95, 95, 95)
        color = tuple(
            int(start + (end - start) * progress)
            for start, end in zip(start_color, end_color)
        )
        Miner.font.draw(
            self.x - camera.x - 24,
            self.y + 62 - camera.y + rise,
            self.notification,
            color,
        )
