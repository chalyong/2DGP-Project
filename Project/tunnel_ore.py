from pico2d import get_time, load_font, load_image
from sdl2 import SDL_KEYDOWN, SDLK_SPACE

import camera
import game_state


class TunnelOre:
    font = None

    def __init__(self, x, y, image_path, player, item_name):
        self.x = x
        self.y = y
        self.player = player
        self.item_name = item_name
        self.notification = None
        self.notification_started = 0
        self.notification_x = 0
        self.notification_y = 0
        self.image = load_image(image_path)
        if TunnelOre.font is None:
            TunnelOre.font = load_font(r"C:\Windows\Fonts\consolab.ttf", 20)

    def handle_event(self, event):
        if (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and abs(self.player.x - self.x) <= 100
            and not self.player.mining
        ):
            amount = 1
            game_state.collected_items[self.item_name] += amount
            self.player.start_mining()
            self.notification = f"{self.item_name.upper()} * {amount}"
            self.notification_started = get_time()
            self.notification_x = self.player.x - 45
            self.notification_y = self.player.y + 55

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x - camera.x, self.y - camera.y, 200, 200)
        if self.notification:
            elapsed = get_time() - self.notification_started
            duration = 1.0
            if elapsed >= duration:
                self.notification = None
                return

            progress = elapsed / duration
            rise = 45 * progress
            start_color = (255, 239, 177)
            end_color = (95, 95, 95)
            color = tuple(
                int(start + (end - start) * progress)
                for start, end in zip(start_color, end_color)
            )
            TunnelOre.font.draw(
                self.notification_x - camera.x,
                self.notification_y - camera.y + rise,
                self.notification,
                color,
            )
