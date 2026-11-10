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
        self.notification_until = 0
        self.image = load_image(image_path)
        if TunnelOre.font is None:
            TunnelOre.font = load_font(r"C:\Windows\Fonts\consolab.ttf", 20)

    def handle_event(self, event):
        if (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and abs(self.player.x - self.x) <= 100
        ):
            amount = 1
            game_state.collected_items[self.item_name] += amount
            self.notification = f"{self.item_name.upper()} * {amount}"
            self.notification_until = get_time() + 1.0

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x - camera.x, self.y - camera.y, 200, 200)
        if self.notification and get_time() < self.notification_until:
            TunnelOre.font.draw(
                self.player.x - camera.x - 45,
                self.player.y - camera.y + 55,
                self.notification,
                (255, 239, 177),
            )
        elif self.notification:
            self.notification = None
